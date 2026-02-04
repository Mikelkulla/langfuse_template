import os


def configure_proxy_and_certs():
    """Set proxy and SSL cert environment variables. Call before any HTTP imports."""
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:8888"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8888"
    os.environ["REQUESTS_KWARGS"] = '{"verify": false}'
    os.environ["SSL_CERT_FILE"] = r"C:\Users\MikelKulla\Desktop\cert.pem"
    os.environ["REQUESTS_CA_BUNDLE"] = r"C:\Users\MikelKulla\Desktop\cert.pem"
    os.environ["CURL_CA_BUNDLE"] = r"C:\Users\MikelKulla\Desktop\cert.pem"


def enable_error_passthrough(tools):
    """Enable error passthrough for all tools to prevent silent failures."""
    for t in tools:
        if hasattr(t, "handle_tool_error"):
            t.handle_tool_error = True
        if hasattr(t, "handle_validation_error"):
            t.handle_validation_error = True
    return tools
