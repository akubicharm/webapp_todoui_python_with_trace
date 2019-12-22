# 環境設定

FUNC_URL : 呼び出すFunctionのURL
INSTRUMENTATION_KEY : ログを送信するApplication Insightsのインストルメントキー


# Flaskアプリをデフォルトの app.py または application.py 以外のファイルから起動する場合は、カスタムGunicornのスタートアップコマンドを指定する。

## hello.py の app を実行する場合
GUNICORN_CMD="gunicorn --bind=0.0.0.0 --timeout 600 hello:myapp"
az webapp config set --resource-group <resource-group-name> --name <app-name> --startup-file $GUNICORN_CMD

https://docs.microsoft.com/ja-jp/azure/app-service/containers/how-to-configure-python#customize-startup-command

https://pypi.org/project/opencensus-ext-azure/
