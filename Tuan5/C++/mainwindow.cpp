#include "mainwindow.h"
#include <QVBoxLayout>
#include <QGridLayout>
#include <QGroupBox>
#include <QLabel>
#include <QMessageBox>
#include <QFileDialog>
#include <QApplication>
#include <QClipboard>
#include <QJsonDocument>
#include <QJsonObject>
#include <QFile>
#include <QTextStream>
#include <QCryptographicHash>
#include <QDateTime>

// ================= CÁC HÀM TOÁN HỌC HỖ TRỢ ELGAMAL =================

bool isPrime(long long n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    for (long long i = 5; i * i <= n; i = i + 6)
        if (n % i == 0 || n % (i + 2) == 0) return false;
    return true;
}

long long gcd(long long a, long long b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

long long extGCD(long long a, long long b, long long &x, long long &y) {
    if (b == 0) { x = 1; y = 0; return a; }
    long long x1, y1;
    long long d = extGCD(b, a % b, x1, y1);
    x = y1;
    y = x1 - y1 * (a / b);
    return d;
}

long long modInverse(long long a, long long m) {
    long long x, y;
    long long g = extGCD(a, m, x, y);
    if (g != 1) return -1;
    return (x % m + m) % m;
}

long long powerMod(long long base, long long exp, long long mod) {
    long long res = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        exp = exp >> 1;
        base = (base * base) % mod;
    }
    return res;
}

// ================= CODE GIAO DIỆN (UI) =================

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
    setWindowTitle("Hệ thống chữ ký số ElGamal (Nhóm 11)");
    resize(1000, 700);
    srand(QDateTime::currentMSecsSinceEpoch());
    setupUI();
}

MainWindow::~MainWindow() {}

void MainWindow::setupUI() {
    QWidget *centralWidget = new QWidget(this);
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

    notebook = new QTabWidget(this);
    mainLayout->addWidget(notebook);

    createKeyTab();
    createSignTab();
    createVerifyTab();

    setCentralWidget(centralWidget);
}

void MainWindow::createKeyTab() {
    QWidget *tabKeys = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(tabKeys);

    QGroupBox *groupInput = new QGroupBox("Nhập tham số ElGamal");
    QGridLayout *gridLayout = new QGridLayout(groupInput);

    gridLayout->addWidget(new QLabel("p (số nguyên tố):"), 0, 0);
    entry_p = new QLineEdit();
    gridLayout->addWidget(entry_p, 0, 1);

    gridLayout->addWidget(new QLabel("x (khóa bí mật):"), 0, 2);
    entry_q = new QLineEdit();
    gridLayout->addWidget(entry_q, 0, 3);

    gridLayout->addWidget(new QLabel("g (căn nguyên thủy):"), 1, 0);
    entry_g = new QLineEdit();
    gridLayout->addWidget(entry_g, 1, 1);

    gridLayout->addWidget(new QLabel("y (khóa công khai):"), 1, 2);
    entry_y = new QLineEdit();
    entry_y->setReadOnly(true);
    gridLayout->addWidget(entry_y, 1, 3);

    QHBoxLayout *btnLayout = new QHBoxLayout();
    QPushButton *btnGen = new QPushButton("Tạo khóa");
    QPushButton *btnAuto = new QPushButton("Sinh khóa tự động");
    QPushButton *btnSave = new QPushButton("Lưu khóa");
    QPushButton *btnLoad = new QPushButton("Tải khóa");

    btnLayout->addWidget(btnGen);
    btnLayout->addWidget(btnAuto);
    btnLayout->addWidget(btnSave);
    btnLayout->addWidget(btnLoad);
    gridLayout->addLayout(btnLayout, 2, 0, 1, 4);

    layout->addWidget(groupInput);

    QGroupBox *groupDisplay = new QGroupBox("Thông tin khóa");
    QVBoxLayout *dispLayout = new QVBoxLayout(groupDisplay);
    text_keys = new QTextEdit();
    text_keys->setReadOnly(true);
    text_keys->setFontFamily("Courier New");
    dispLayout->addWidget(text_keys);
    layout->addWidget(groupDisplay);

    notebook->addTab(tabKeys, "1. Sinh khóa");

    connect(btnGen, &QPushButton::clicked, this, &MainWindow::generateKeys);
    connect(btnAuto, &QPushButton::clicked, this, &MainWindow::autoGenerateKeys);
    connect(btnSave, &QPushButton::clicked, this, &MainWindow::saveKeys);
    connect(btnLoad, &QPushButton::clicked, this, &MainWindow::loadKeys);
}

void MainWindow::createSignTab() {
    QWidget *tabSign = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(tabSign);

    QGroupBox *groupInput = new QGroupBox("Nhập dữ liệu cần ký");
    QVBoxLayout *inputLayout = new QVBoxLayout(groupInput);
    text_message = new QTextEdit();
    inputLayout->addWidget(text_message);

    QHBoxLayout *btnLayout = new QHBoxLayout();
    QPushButton *btnSign = new QPushButton("Tạo chữ ký");
    QPushButton *btnClear = new QPushButton("Xóa");
    QPushButton *btnSaveMsg = new QPushButton("Lưu dữ liệu");
    QPushButton *btnLoadMsg = new QPushButton("Tải dữ liệu");

    btnLayout->addWidget(btnSign);
    btnLayout->addWidget(btnClear);
    btnLayout->addWidget(btnSaveMsg);
    btnLayout->addWidget(btnLoadMsg);
    inputLayout->addLayout(btnLayout);
    layout->addWidget(groupInput);

    QGroupBox *groupSig = new QGroupBox("Chữ kí số là:");
    QVBoxLayout *sigLayout = new QVBoxLayout(groupSig);
    text_signature = new QTextEdit();
    sigLayout->addWidget(text_signature);

    QHBoxLayout *btnLayout2 = new QHBoxLayout();
    QPushButton *btnSaveSig = new QPushButton("Lưu chữ ký");
    QPushButton *btnCopySig = new QPushButton("Sao chép chữ ký");

    btnLayout2->addWidget(btnSaveSig);
    btnLayout2->addWidget(btnCopySig);
    sigLayout->addLayout(btnLayout2);
    layout->addWidget(groupSig);

    notebook->addTab(tabSign, "2. Tạo chữ ký");

    connect(btnSign, &QPushButton::clicked, this, &MainWindow::createSignature);
    connect(btnClear, &QPushButton::clicked, text_message, &QTextEdit::clear);
    connect(btnSaveMsg, &QPushButton::clicked, this, &MainWindow::saveMessage);
    connect(btnLoadMsg, &QPushButton::clicked, this, &MainWindow::loadMessage);
    connect(btnSaveSig, &QPushButton::clicked, this, &MainWindow::saveSignature);
    connect(btnCopySig, &QPushButton::clicked, this, &MainWindow::copySignature);
}

void MainWindow::createVerifyTab() {
    QWidget *tabVerify = new QWidget();
    QVBoxLayout *layout = new QVBoxLayout(tabVerify);

    QGroupBox *groupInput = new QGroupBox("Xác nhận chữ kí số");
    QVBoxLayout *inputLayout = new QVBoxLayout(groupInput);

    // Dòng chứa nhãn và nút tải Văn bản (MỚI BỔ SUNG)
    QHBoxLayout *msgLabelLayout = new QHBoxLayout();
    msgLabelLayout->addWidget(new QLabel("Dữ liệu cần ký:"));
    QPushButton *btnLoadMsgVerify = new QPushButton("Tải dữ liệu");
    msgLabelLayout->addWidget(btnLoadMsgVerify);
    msgLabelLayout->addStretch();
    inputLayout->addLayout(msgLabelLayout);

    text_verify_message = new QTextEdit();
    inputLayout->addWidget(text_verify_message);

    // Dòng chứa nhãn và nút tải Chữ ký (MỚI BỔ SUNG)
    QHBoxLayout *sigLabelLayout = new QHBoxLayout();
    sigLabelLayout->addWidget(new QLabel("Chữ ký (định dạng JSON):"));
    QPushButton *btnLoadSigVerify = new QPushButton("Tải chữ ký");
    sigLabelLayout->addWidget(btnLoadSigVerify);
    sigLabelLayout->addStretch();
    inputLayout->addLayout(sigLabelLayout);

    text_verify_signature = new QTextEdit();
    inputLayout->addWidget(text_verify_signature);

    QPushButton *btnVerify = new QPushButton("Xác minh");
    inputLayout->addWidget(btnVerify);
    layout->addWidget(groupInput);

    QGroupBox *groupResult = new QGroupBox("Kết quả xác minh");
    QVBoxLayout *resLayout = new QVBoxLayout(groupResult);
    text_verify_result = new QTextEdit();
    text_verify_result->setReadOnly(true);
    resLayout->addWidget(text_verify_result);
    layout->addWidget(groupResult);

    notebook->addTab(tabVerify, "3. Xác minh chữ ký");

    // Kết nối các nút mới ở Tab 3
    connect(btnVerify, &QPushButton::clicked, this, &MainWindow::verifySignature);
    connect(btnLoadMsgVerify, &QPushButton::clicked, this, &MainWindow::loadMessageForVerify);
    connect(btnLoadSigVerify, &QPushButton::clicked, this, &MainWindow::loadSignatureForVerify);
}

// ================= LOGIC TOÁN HỌC & XỬ LÝ CHÍNH =================

void MainWindow::generateKeys() {
    QString p_str = entry_p->text();
    QString g_str = entry_g->text();
    QString x_str = entry_q->text();

    if (p_str.isEmpty() || g_str.isEmpty() || x_str.isEmpty()) {
        QMessageBox::warning(this, "Lỗi", "Vui lòng nhập đầy đủ p, g, và x!"); return;
    }

    long long p_val = p_str.toLongLong();
    long long g_val = g_str.toLongLong();
    long long x_val = x_str.toLongLong();

    if (p_val <= 1 || !isPrime(p_val)) {
        QMessageBox::warning(this, "Lỗi Điều Kiện", "p phải là số nguyên tố lớn hơn 1!"); return;
    }
    if (g_val <= 0 || g_val >= p_val || x_val <= 0 || x_val >= p_val) {
        QMessageBox::warning(this, "Lỗi Điều Kiện", "g và x phải nằm trong khoảng (0, p)!"); return;
    }

    long long y_val = powerMod(g_val, x_val, p_val);
    entry_y->setText(QString::number(y_val));

    QString info = "Tạo khóa thành công!\n";
    info += "p = " + p_str + "\n" + "g = " + g_str + "\n" + "x = " + x_str + "\n" + "y = " + QString::number(y_val) + "\n";
    text_keys->setText(info);
}

void MainWindow::autoGenerateKeys() {
    entry_p->setText("10631");
    entry_g->setText("11");
    entry_q->setText("1831");
    generateKeys();
    QMessageBox::information(this, "Thành công", "Đã tự động sinh tham số mẫu!");
}

void MainWindow::createSignature() {
    QString msg = text_message->toPlainText();
    if (msg.isEmpty() || entry_y->text().isEmpty()) {
        QMessageBox::warning(this, "Lỗi", "Vui lòng sinh khóa và nhập dữ liệu cần ký!"); return;
    }

    long long p_val = entry_p->text().toLongLong();
    long long g_val = entry_g->text().toLongLong();
    long long x_val = entry_q->text().toLongLong();

    QString hashHex = QString(QCryptographicHash::hash(msg.toUtf8(), QCryptographicHash::Sha256).toHex());

    long long H_val = hashHex.left(12).toLongLong(nullptr, 16) % (p_val - 1);
    if (H_val == 0) H_val = 1;

    long long k;
    do {
        k = rand() % (p_val - 2) + 1;
    } while (gcd(k, p_val - 1) != 1);

    long long r = powerMod(g_val, k, p_val);

    long long temp = (H_val - (x_val * r) % (p_val - 1)) % (p_val - 1);
    if (temp < 0) temp += (p_val - 1);
    long long k_inv = modInverse(k, p_val - 1);
    long long s = (temp * k_inv) % (p_val - 1);

    if (s == 0) {
        createSignature();
        return;
    }

    QJsonObject sigJson;
    sigJson["r"] = QString::number(r);
    sigJson["s"] = QString::number(s);
    sigJson["hash"] = hashHex;

    QJsonDocument doc(sigJson);
    text_signature->setText(doc.toJson(QJsonDocument::Indented));
    QMessageBox::information(this, "Thành công", "Đã tạo chữ ký số dựa trên SHA-256!");
}

void MainWindow::verifySignature() {
    QString currentMsg = text_verify_message->toPlainText();
    QString sigText = text_verify_signature->toPlainText();

    if (currentMsg.isEmpty() || sigText.isEmpty() || entry_p->text().isEmpty()) {
        QMessageBox::warning(this, "Lỗi", "Vui lòng nhập đủ Khóa, Văn bản và Chữ ký!"); return;
    }

    long long p_val = entry_p->text().toLongLong();
    long long g_val = entry_g->text().toLongLong();
    long long y_val = entry_y->text().toLongLong();

    QJsonDocument doc = QJsonDocument::fromJson(sigText.toUtf8());
    if (doc.isNull() || !doc.isObject()) {
        QMessageBox::critical(this, "Lỗi", "Định dạng chữ ký không đúng (phải là JSON)!"); return;
    }

    QJsonObject sigJson = doc.object();
    long long r = sigJson["r"].toString().toLongLong();
    long long s = sigJson["s"].toString().toLongLong();
    QString origHashHex = sigJson["hash"].toString();

    QString currentHashHex = QString(QCryptographicHash::hash(currentMsg.toUtf8(), QCryptographicHash::Sha256).toHex());

    bool isTextIntact = (currentHashHex == origHashHex);

    long long H_orig_val = origHashHex.left(12).toLongLong(nullptr, 16) % (p_val - 1);
    if (H_orig_val == 0) H_orig_val = 1;

    bool isSigIntact = false;
    if (r > 0 && r < p_val && s > 0 && s < p_val - 1) {
        long long v1 = (powerMod(y_val, r, p_val) * powerMod(r, s, p_val)) % p_val;
        long long v2 = powerMod(g_val, H_orig_val, p_val);
        if (v1 == v2) isSigIntact = true;
    }

    QString resultText = "=== BÁO CÁO KẾT QUẢ THẨM ĐỊNH ===\n\n";

    if (isTextIntact && isSigIntact) {
        resultText += "✅ HỢP LỆ: Văn bản gốc và Chữ ký số đều an toàn, không bị chỉnh sửa.";
    }
    else if (!isTextIntact && isSigIntact) {
        resultText += "❌ LỖI TÌNH HUỐNG 1:\n-> VĂN BẢN BỊ SỬA ĐỔI (Hash không khớp, nhưng chữ ký thì đúng với Hash gốc).";
    }
    else if (isTextIntact && !isSigIntact) {
        resultText += "❌ LỖI TÌNH HUỐNG 2:\n-> CHỮ KÝ BỊ SỬA ĐỔI (Văn bản còn nguyên, nhưng giá trị r hoặc s đã bị thay đổi).";
    }
    else {
        resultText += "❌ LỖI TÌNH HUỐNG 3:\n-> CẢ VĂN BẢN VÀ CHỮ KÝ BỊ SỬA ĐỔI (Hash sai lệch và r, s cũng bị phá hỏng).";
    }

    text_verify_result->setText(resultText);
}

// ================= CÁC HÀM LƯU / TẢI FILE =================

void MainWindow::saveKeys() {
    if (entry_y->text().isEmpty()) {
        QMessageBox::warning(this, "Lỗi", "Chưa có khóa để lưu!"); return;
    }

    // Cho phép người dùng chọn cả đuôi .docx
    QString fileName = QFileDialog::getSaveFileName(this, "Lưu Khóa", "",
                                                    "All Files (*);;Word Document (*.docx);;Text Files (*.txt)");
    if (fileName.isEmpty()) return;

    QFile file(fileName);
    if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QTextStream out(&file);

        // Nếu người dùng chọn lưu đuôi .docx, ta xuất nội dung dạng HTML
        if (fileName.endsWith(".docx", Qt::CaseInsensitive)) {
            out << "<html><body>";
            out << "<h2>THONG TIN KHOA ELGAMAL</h2>";
            out << "<p>p = " << entry_p->text() << "</p>";
            out << "<p>g = " << entry_g->text() << "</p>";
            out << "<p>x = " << entry_q->text() << "</p>";
            out << "<p>y = " << entry_y->text() << "</p>";
            out << "</body></html>";
        } else {
            // Lưu dạng text thuần như cũ
            out << "p=" << entry_p->text() << "\n" << "g=" << entry_g->text() << "\n"
                << "x=" << entry_q->text() << "\n" << "y=" << entry_y->text() << "\n";
        }

        file.close();
        QMessageBox::information(this, "Thành công", "Lưu file thành công!");
    }
}

void MainWindow::loadKeys() {
    QString fileName = QFileDialog::getOpenFileName(this, "Tải Khóa", "", "All Files (*);;Text Files (*.txt)");
    if (fileName.isEmpty()) return;
    QFile file(fileName);
    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QTextStream in(&file);
        while (!in.atEnd()) {
            QString line = in.readLine();
            if (line.startsWith("p=")) entry_p->setText(line.mid(2));
            else if (line.startsWith("g=")) entry_g->setText(line.mid(2));
            else if (line.startsWith("x=")) entry_q->setText(line.mid(2));
            else if (line.startsWith("y=")) entry_y->setText(line.mid(2));
        }
        file.close();
    }
}

void MainWindow::saveMessage() {
    QString msg = text_message->toPlainText();
    if (msg.isEmpty()) return;
    QString fileName = QFileDialog::getSaveFileName(this, "Lưu Văn Bản", "", "All Files (*);;Text Files (*.txt)");
    if (fileName.isEmpty()) return;
    QFile file(fileName);
    if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QTextStream out(&file); out << msg; file.close();
        QMessageBox::information(this, "Thành công", "Đã lưu văn bản!");
    }
}

void MainWindow::loadMessage() {
    QString fileName = QFileDialog::getOpenFileName(this, "Tải Văn Bản", "", "All Files (*);;Text Files (*.txt)");
    if (fileName.isEmpty()) return;
    QFile file(fileName);
    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QTextStream in(&file); text_message->setText(in.readAll()); file.close();
    }
}

void MainWindow::saveSignature() {
    QString sig = text_signature->toPlainText();
    if (sig.isEmpty()) return;
    QString fileName = QFileDialog::getSaveFileName(this, "Lưu Chữ Ký", "", "All Files (*);;JSON Files (*.json);;Text Files (*.txt)");
    if (fileName.isEmpty()) return;
    QFile file(fileName);
    if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        QTextStream out(&file); out << sig; file.close();
        QMessageBox::information(this, "Thành công", "Đã lưu chữ ký!");
    }
}

void MainWindow::copySignature() {
    QClipboard *clipboard = QGuiApplication::clipboard();
    clipboard->setText(text_signature->toPlainText());
    QMessageBox::information(this, "Thành công", "Đã chép chữ ký vào khay nhớ tạm!");
}

// 2 HÀM MỚI ĐỂ TẢI FILE Ở TAB 3
void MainWindow::loadMessageForVerify() {
    QString fileName = QFileDialog::getOpenFileName(this, "Tải Văn Bản Cần Xác Minh", "", "All Files (*);;Text Files (*.txt)");
    if (fileName.isEmpty()) return;
    QFile file(fileName);
    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QTextStream in(&file); text_verify_message->setText(in.readAll()); file.close();
    }
}

void MainWindow::loadSignatureForVerify() {
    QString fileName = QFileDialog::getOpenFileName(this, "Tải Chữ Ký Cần Xác Minh", "", "All Files (*);;JSON Files (*.json);;Text Files (*.txt)");
    if (fileName.isEmpty()) return;
    QFile file(fileName);
    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QTextStream in(&file); text_verify_signature->setText(in.readAll()); file.close();
    }
}