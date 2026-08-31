import UIKit
import WebKit

class ViewController: UIViewController {
    var webView: WKWebView!
    var loadingIndicator: UIActivityIndicatorView!
    var errorView: UIView!
    var errorLabel: UILabel!
    var retryButton: UIButton!

    override func loadView() {
        let config = WKWebViewConfiguration()
        config.preferences.javaScriptEnabled = true
        config.preferences.javaScriptCanOpenWindowsAutomatically = true
        webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        setupLoadingUI()
        setupErrorUI()
        loadPage()
    }

    func loadPage() {
        // 优先加载打包进 App 的本地 index.html(本地页秒开,避免白屏;
        // 页面内 iframe 再加载远程 onrender,加载中由本地页提示)
        if let localURL = Bundle.main.url(forResource: "index", withExtension: "html") {
            webView.loadFileURL(localURL,
                                allowingReadAccessTo: localURL.deletingLastPathComponent())
        } else if let u = URL(string: "https://jr-staff-center.onrender.com/") {
            webView.load(URLRequest(url: u))
        }
    }

    // MARK: - 加载指示(onrender 冷启动可能 20s+,必须给用户反馈)
    func setupLoadingUI() {
        loadingIndicator = UIActivityIndicatorView(style: .large)
        loadingIndicator.center = CGPoint(x: view.bounds.midX, y: view.bounds.midY)
        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.autoresizingMask = [.flexibleLeftMargin, .flexibleRightMargin,
                                             .flexibleTopMargin, .flexibleBottomMargin]
        view.addSubview(loadingIndicator)
        loadingIndicator.startAnimating()
    }

    // MARK: - 加载失败提示 + 重试(避免永久白屏)
    func setupErrorUI() {
        errorView = UIView(frame: view.bounds)
        errorView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        errorView.backgroundColor = .white
        errorView.isHidden = true

        errorLabel = UILabel()
        errorLabel.text = "页面加载失败\n请检查网络后重试"
        errorLabel.numberOfLines = 0
        errorLabel.textAlignment = .center
        errorLabel.font = UIFont.systemFont(ofSize: 16)
        errorLabel.textColor = .darkGray
        errorLabel.translatesAutoresizingMaskIntoConstraints = false

        retryButton = UIButton(type: .system)
        retryButton.setTitle("重新加载", for: .normal)
        retryButton.titleLabel?.font = UIFont.systemFont(ofSize: 17, weight: .semibold)
        retryButton.addTarget(self, action: #selector(retryTapped), for: .touchUpInside)
        retryButton.translatesAutoresizingMaskIntoConstraints = false

        errorView.addSubview(errorLabel)
        errorView.addSubview(retryButton)
        view.addSubview(errorView)

        NSLayoutConstraint.activate([
            errorLabel.centerXAnchor.constraint(equalTo: errorView.centerXAnchor),
            errorLabel.centerYAnchor.constraint(equalTo: errorView.centerYAnchor, constant: -24),
            retryButton.centerXAnchor.constraint(equalTo: errorView.centerXAnchor),
            retryButton.topAnchor.constraint(equalTo: errorLabel.bottomAnchor, constant: 20),
        ])
    }

    @objc func retryTapped() {
        errorView.isHidden = true
        loadingIndicator.startAnimating()
        loadPage()
    }
}

// MARK: - WKNavigationDelegate
extension ViewController: WKNavigationDelegate, WKUIDelegate {
    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
        loadingIndicator.startAnimating()
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        loadingIndicator.stopAnimating()
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        loadingIndicator.stopAnimating()
        errorView.isHidden = false
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        loadingIndicator.stopAnimating()
        // -999 是页面被替换/跳转的取消错误,不算失败
        if (error as NSError).code != NSURLErrorCancelled {
            errorView.isHidden = false
        }
    }
}
