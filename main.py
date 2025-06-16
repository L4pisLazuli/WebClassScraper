from webclass_client import WebClassClient
from datetime import datetime
import dotenv
from pathlib import Path
import json
import sys
import logging
from logging.handlers import RotatingFileHandler

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'output/webclass.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_execution_limit():
    """1日1回の実行制限をチェックする関数"""
    try:
        # 実行履歴ファイルのパス
        history_file = Path("output/execution_history.json")
        
        # 現在の日付
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 実行履歴の読み込み
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except json.JSONDecodeError:
                logger.error("実行履歴ファイルの読み込みに失敗しました")
                history = {}
        else:
            history = {}
        
        # 最後の実行日をチェック
        last_execution = history.get("last_execution")
        if last_execution == today:
            logger.warning("本日は既に実行済みです")
            print("エラー: 本日は既に実行済みです。")
            print("次回の実行は明日以降にしてください。")
            sys.exit(1)
        
        # 実行履歴を更新
        history["last_execution"] = today
        history_file.parent.mkdir(exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        logger.info(f"実行履歴を更新しました: {today}")
    except Exception as e:
        logger.error(f"実行制限チェック中にエラーが発生しました: {e}")
        raise

def generate_html(assignments, messages_with_subject):
    try:
        # 重複を排除し、期限順にソート
        unique_assignments = []
        seen = set()
        for assignment in assignments:
            key = f"{assignment.get('subject')}_{assignment.get('name')}"
            if key not in seen:
                seen.add(key)
                unique_assignments.append(assignment)
        
        # 期限順にソート
        unique_assignments.sort(key=lambda x: x.get('availability_period_to', '9999/99/99 99:99'))
        
        logger.info(f"課題数: {len(unique_assignments)}")
        logger.info(f"お知らせ数: {len(messages_with_subject)}")
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>WebClass情報</title>
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
            <style>
                :root {
                    --md-sys-color-primary: #0061a4;
                    --md-sys-color-primary-container: #d1e4ff;
                    --md-sys-color-secondary: #535f70;
                    --md-sys-color-secondary-container: #d7e3f8;
                    --md-sys-color-tertiary: #6b5778;
                    --md-sys-color-tertiary-container: #f3daff;
                    --md-sys-color-error: #ba1a1a;
                    --md-sys-color-error-container: #ffdad6;
                    --md-sys-color-surface: #fdfcff;
                    --md-sys-color-surface-variant: #dfe2eb;
                    --md-sys-color-outline: #73777f;
                    --md-sys-color-outline-variant: #c3c7cf;
                    --md-sys-color-shadow: #000000;
                    --md-sys-color-scrim: #000000;
                    --md-sys-color-inverse-surface: #2f3033;
                    --md-sys-color-inverse-on-surface: #f1f0f4;
                    --md-sys-color-inverse-primary: #9fcaee;
                    --md-sys-color-surface-tint: #0061a4;
                    --md-sys-color-on-primary: #ffffff;
                    --md-sys-color-on-primary-container: #001d36;
                    --md-sys-color-on-secondary: #ffffff;
                    --md-sys-color-on-secondary-container: #101c2b;
                    --md-sys-color-on-tertiary: #ffffff;
                    --md-sys-color-on-tertiary-container: #251431;
                    --md-sys-color-on-error: #ffffff;
                    --md-sys-color-on-error-container: #410002;
                    --md-sys-color-on-surface: #1a1c1e;
                    --md-sys-color-on-surface-variant: #43474e;
                    --md-sys-color-on-inverse-surface: #f1f0f4;
                    --md-sys-color-on-inverse-primary: #003258;
                    --md-sys-color-surface-container-lowest: #ffffff;
                    --md-sys-color-surface-container-low: #f7f7fa;
                    --md-sys-color-surface-container: #f2f2f5;
                    --md-sys-color-surface-container-high: #eceef0;
                    --md-sys-color-surface-container-highest: #e6e8eb;
                }
                
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Noto Sans JP', sans-serif;
                    background-color: var(--md-sys-color-surface-container-low);
                    color: var(--md-sys-color-on-surface);
                    line-height: 1.6;
                    min-height: 100vh;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                
                .header {
                    background-color: var(--md-sys-color-primary);
                    color: var(--md-sys-color-on-primary);
                    padding: 2rem 0;
                    margin-bottom: 2rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .header h1 {
                    text-align: center;
                    font-size: 2rem;
                    font-weight: 700;
                }
                
                .section {
                    background-color: var(--md-sys-color-surface);
                    border-radius: 1rem;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                
                h2 {
                    color: var(--md-sys-color-primary);
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    padding-bottom: 0.5rem;
                    border-bottom: 2px solid var(--md-sys-color-primary-container);
                }
                
                .assignment {
                    background-color: var(--md-sys-color-surface);
                    border: 1px solid var(--md-sys-color-outline-variant);
                    border-radius: 0.75rem;
                    padding: 1.25rem;
                    margin: 1rem 0;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }
                
                .assignment:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                
                .assignment::before {
                    content: '';
                    position: absolute;
                    left: 0;
                    top: 0;
                    bottom: 0;
                    width: 4px;
                    background-color: var(--md-sys-color-primary);
                    opacity: 0;
                    transition: opacity 0.3s ease;
                }
                
                .assignment:hover::before {
                    opacity: 1;
                }
                
                .checkbox {
                    appearance: none;
                    -webkit-appearance: none;
                    width: 1.5rem;
                    height: 1.5rem;
                    border: 2px solid var(--md-sys-color-outline);
                    border-radius: 0.25rem;
                    margin-right: 1rem;
                    position: relative;
                    cursor: pointer;
                    vertical-align: middle;
                    transition: all 0.2s ease;
                }
                
                .checkbox:checked {
                    background-color: var(--md-sys-color-primary);
                    border-color: var(--md-sys-color-primary);
                }
                
                .checkbox:checked::after {
                    content: '✓';
                    position: absolute;
                    color: white;
                    font-size: 1rem;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                }
                
                .subject {
                    color: var(--md-sys-color-primary);
                    font-weight: 700;
                    font-size: 1.1rem;
                    display: block;
                    margin-bottom: 0.5rem;
                }
                
                .title {
                    font-size: 1.2rem;
                    font-weight: 500;
                    margin: 0.5rem 0;
                    color: var(--md-sys-color-on-surface);
                }
                
                .category {
                    display: inline-block;
                    padding: 0.25rem 0.75rem;
                    background-color: var(--md-sys-color-secondary-container);
                    color: var(--md-sys-color-on-secondary-container);
                    border-radius: 1rem;
                    font-size: 0.875rem;
                    font-weight: 500;
                    margin: 0.5rem 0;
                }
                
                .due-date {
                    color: var(--md-sys-color-on-surface-variant);
                    font-size: 0.875rem;
                    margin-top: 0.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .due-date::before {
                    content: '⏰';
                    font-size: 1rem;
                }
                
                .message {
                    background-color: var(--md-sys-color-surface);
                    border: 1px solid var(--md-sys-color-outline-variant);
                    border-radius: 0.75rem;
                    padding: 1.25rem;
                    margin: 1rem 0;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }
                
                .message:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                
                .message.read {
                    opacity: 0.7;
                    background-color: var(--md-sys-color-surface-container);
                }
                
                .message.unread {
                    border-left: 4px solid var(--md-sys-color-primary);
                }
                
                .message-subject {
                    color: var(--md-sys-color-primary);
                    font-weight: 700;
                    font-size: 1.1rem;
                    margin-bottom: 0.5rem;
                    display: block;
                }
                
                .message-content {
                    color: var(--md-sys-color-on-surface);
                    font-size: 1rem;
                    line-height: 1.6;
                    margin-top: 0.5rem;
                }
                
                .message-divider {
                    height: 1px;
                    background-color: var(--md-sys-color-outline-variant);
                    margin: 0.5rem 0;
                }
                
                .urgent {
                    border-left: 4px solid var(--md-sys-color-error);
                }
                
                .warning {
                    border-left: 4px solid var(--md-sys-color-tertiary);
                }
                
                .assignment.completed {
                    opacity: 0.6;
                    background-color: var(--md-sys-color-surface-container);
                }
                
                .assignment.completed .title {
                    text-decoration: line-through;
                }
                
                .assignment.uncompleted {
                    border-left: 4px solid var(--md-sys-color-primary);
                }
                
                @media (max-width: 768px) {
                    .container {
                        padding: 1rem;
                    }
                    
                    .header {
                        padding: 1.5rem 0;
                    }
                    
                    .header h1 {
                        font-size: 1.5rem;
                    }
                    
                    .section {
                        padding: 1rem;
                    }
                    
                    .assignment, .message {
                        padding: 1rem;
                    }
                }
            </style>
            <script>
                // 課題の状態を保存する関数
                function saveState(assignmentId, isCompleted) {
                    // ローカルストレージに保存
                    const states = JSON.parse(localStorage.getItem('assignment_states') || '{}');
                    states[assignmentId] = isCompleted;
                    localStorage.setItem('assignment_states', JSON.stringify(states));
                    
                    // カードの見た目を更新
                    const card = document.querySelector(`[data-assignment-id="${assignmentId}"]`);
                    if (card) {
                        card.classList.toggle('completed', isCompleted);
                        card.classList.toggle('uncompleted', !isCompleted);
                    }
                    
                    // 課題の順序を更新
                    sortAssignments();
                }

                // 課題の状態を復元する関数
                function restoreStates() {
                    const states = JSON.parse(localStorage.getItem('assignment_states') || '{}');
                    Object.entries(states).forEach(([assignmentId, isCompleted]) => {
                        const card = document.querySelector(`[data-assignment-id="${assignmentId}"]`);
                        if (card) {
                            card.classList.toggle('completed', isCompleted);
                            card.classList.toggle('uncompleted', !isCompleted);
                            const checkbox = card.querySelector('.assignment-checkbox');
                            if (checkbox) {
                                checkbox.checked = isCompleted;
                            }
                        }
                    });
                    
                    // 初期表示時に課題をソート
                    sortAssignments();
                }

                // 課題をソートする関数
                function sortAssignments() {
                    const container = document.querySelector('.assignments');
                    const assignments = Array.from(container.children);
                    
                    assignments.sort((a, b) => {
                        const aCompleted = a.classList.contains('completed');
                        const bCompleted = b.classList.contains('completed');
                        
                        if (aCompleted === bCompleted) {
                            // 同じ状態の場合は期限でソート
                            const aDueDate = a.querySelector('.due-date').textContent;
                            const bDueDate = b.querySelector('.due-date').textContent;
                            return aDueDate.localeCompare(bDueDate);
                        }
                        
                        // 未完了を上に
                        return aCompleted ? 1 : -1;
                    });
                    
                    // ソートした要素を再配置
                    assignments.forEach(assignment => container.appendChild(assignment));
                }

                // お知らせの未読状態を管理する関数
                function markMessageAsRead(messageId) {
                    const readMessages = JSON.parse(localStorage.getItem('read_messages') || '{}');
                    readMessages[messageId] = true;
                    localStorage.setItem('read_messages', JSON.stringify(readMessages));
                    
                    // メッセージカードの見た目を更新
                    const card = document.querySelector(`[data-message-id="${messageId}"]`);
                    if (card) {
                        card.classList.add('read');
                    }
                }

                // お知らせの状態を復元する関数
                function restoreMessageStates() {
                    const readMessages = JSON.parse(localStorage.getItem('read_messages') || '{}');
                    document.querySelectorAll('.message').forEach(card => {
                        const messageId = card.getAttribute('data-message-id');
                        if (readMessages[messageId]) {
                            card.classList.add('read');
                        }
                    });
                }

                // ページ読み込み時に状態を復元
                document.addEventListener('DOMContentLoaded', function() {
                    restoreStates();
                    restoreMessageStates();
                });

                // チェックボックスの変更を監視
                document.addEventListener('change', function(e) {
                    if (e.target.classList.contains('assignment-checkbox')) {
                        const card = e.target.closest('.assignment');
                        const assignmentId = card.getAttribute('data-assignment-id');
                        saveState(assignmentId, e.target.checked);
                    }
                });

                // メッセージのクリックを監視
                document.addEventListener('click', function(e) {
                    const messageCard = e.target.closest('.message');
                    if (messageCard) {
                        const messageId = messageCard.getAttribute('data-message-id');
                        markMessageAsRead(messageId);
                    }
                });
            </script>
        </head>
        <body>
            <div class="header">
                <div class="container">
                    <h1>WebClass情報</h1>
                </div>
            </div>
            
            <div class="container">
                <div class="section">
                    <h2>課題一覧</h2>
                    <div class="assignments">
        """
        
        for i, assignment in enumerate(unique_assignments):
            due_date = assignment.get('availability_period_to', '')
            is_urgent = False
            is_warning = False
            
            try:
                due_dt = datetime.strptime(due_date, "%Y/%m/%d %H:%M")
                now = datetime.now()
                days_left = (due_dt - now).days
                
                if days_left <= 3:
                    is_urgent = True
                elif days_left <= 7:
                    is_warning = True
            except:
                pass
            
            urgency_class = "urgent" if is_urgent else "warning" if is_warning else ""
            assignment_id = f"{assignment.get('subject', '')}_{assignment.get('name', '')}"
            
            html += f"""
                <div class="assignment {urgency_class} uncompleted" data-assignment-id="{assignment_id}">
                    <input type="checkbox" class="checkbox assignment-checkbox">
                    <span class="subject">{assignment.get('subject', '')}</span>
                    <span class="title">{assignment.get('name', '')}</span>
                    <span class="category">{assignment.get('category', '')}</span>
                    <div class="due-date">期限: {due_date}</div>
                </div>
            """
        
        html += """
                    </div>
                </div>
                
                <div class="section">
                    <h2>お知らせ一覧</h2>
                    <div class="messages">
        """
        
        # お知らせを科目名でソート
        messages_with_subject.sort(key=lambda x: x[0])
        
        for subject, message in messages_with_subject:
            message_id = f"{subject}_{message}"
            html += f"""
                <div class="message" data-message-id="{message_id}">
                    <span class="message-subject">{subject}</span>
                    <div class="message-divider"></div>
                    <p class="message-content">{message}</p>
                </div>
            """
        
        html += """
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        logger.error(f"HTML生成中にエラーが発生しました: {e}")
        raise

if __name__ == "__main__":
    try:
        # 出力ディレクトリの作成
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # 実行制限のチェック
        check_execution_limit()
        
        url = "https://els.sa.dendai.ac.jp"
        dotenv.load_dotenv()
        username = dotenv.get_key(".env", "USERNAME")
        password = dotenv.get_key(".env", "PASSWORD")
        
        if not username or not password:
            logger.error("環境変数 USERNAME または PASSWORD が設定されていません")
            print("エラー: 環境変数が設定されていません。")
            print(".envファイルを確認してください。")
            sys.exit()

        client = WebClassClient(url)
        client.set_login_info(username, password)
        
        if client.login():
            logger.info("ログイン成功")
            
            # 課題情報の取得とHTML生成
            assignment_info = client.get_assignment_info(datetime.now())
            logger.info(f"課題情報を取得しました: {len(assignment_info)}件")

            # お知らせの取得
            lecture_ids = client.get_lecture_id_list()
            messages_with_subject = []
            for lecture_id in lecture_ids:
                subject = client.get_lecture_name(lecture_id)
                messages = client.get_lecture_message(lecture_id, "2000-01-01")
                for message in messages:
                    messages_with_subject.append((subject, message))
            
            logger.info(f"お知らせを取得しました: {len(messages_with_subject)}件")
            
            # HTML生成と保存
            html_content = generate_html(assignment_info, messages_with_subject)
            output_file = output_dir / "webclass_info.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"HTMLファイルを生成しました: {output_file}")
            print("HTMLファイルを生成しました。")
            print(f"出力先: {output_file}")

            client.logout()
            logger.info("ログアウト完了")
        else:
            logger.error("ログインに失敗しました")
            print("ログインに失敗しました。")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {e}")
        print("エラーが発生しました。")
        print("詳細はログファイルを確認してください。")
        sys.exit(1)
