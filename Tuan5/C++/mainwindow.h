#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTabWidget>
#include <QLineEdit>
#include <QTextEdit>
#include <QPushButton>

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void generateKeys();
    void autoGenerateKeys();
    void createSignature();
    void verifySignature();

    // Các hàm File I/O Tab 1 & 2
    void saveKeys();
    void loadKeys();
    void saveMessage();
    void loadMessage();
    void saveSignature();
    void copySignature();

    // Các hàm File I/O Tab 3 (MỚI BỔ SUNG)
    void loadMessageForVerify();
    void loadSignatureForVerify();

private:
    void setupUI();
    void createKeyTab();
    void createSignTab();
    void createVerifyTab();

    QTabWidget *notebook;

    QLineEdit *entry_p;
    QLineEdit *entry_q;
    QLineEdit *entry_g;
    QLineEdit *entry_y;
    QTextEdit *text_keys;

    QTextEdit *text_message;
    QTextEdit *text_signature;

    QTextEdit *text_verify_message;
    QTextEdit *text_verify_signature;
    QTextEdit *text_verify_result;
};

#endif // MAINWINDOW_H