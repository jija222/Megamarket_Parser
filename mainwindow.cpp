#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QProcess>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QDebug>
#include <QString>
#include <QFile>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    connect(ui->startParsing, &QPushButton::clicked, this, &MainWindow::on_startButton_clicked);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_startButton_clicked() {
    QString url = ui->inputCategory->toPlainText().trimmed();
    QString pagesStr = ui->inputPages->toPlainText().trimmed();

    bool ok;
    int pages = pagesStr.toInt(&ok);
    if (url.isEmpty() || !ok || pages < 1) {
        ui->outputInfo->setPlainText("Введите корректные данные: URL и количество страниц");
        ui->outputInfo->repaint(); // Принудительно перерисовать
        QApplication::processEvents();
        return;
    }

    QString filePath = QCoreApplication::applicationDirPath() + "/url.txt";
    QFile file(filePath);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate)) {
        ui->outputInfo->insertPlainText("Не удалось открыть файл для записи URL");
        ui->outputInfo->repaint(); // Принудительно перерисовать
        QApplication::processEvents();
        return;
    }
    QTextStream out(&file);
    out << url;
    file.close();

    QProcess process;
    process.setWorkingDirectory(QCoreApplication::applicationDirPath());
    QStringList arguments;

    arguments << "C:\\Users\\User\\Documents\\QT_Creator\\Megamarket\\Parsesr\\ParserGui\\ParserUTF8.py" << QString::number(pages);

    process.start("python", arguments);
    if (!process.waitForStarted()) {
        ui->outputInfo->insertPlainText("Ошибка запуска Python-скрипта");
        ui->outputInfo->repaint(); // Принудительно перерисовать
        QApplication::processEvents();
        return;
    }

    process.closeWriteChannel();
    process.waitForFinished(-1);

    QByteArray output = process.readAllStandardOutput();
    QByteArray error = process.readAllStandardError();

    if (!error.isEmpty()) {
        ui->outputInfo->insertPlainText("Ошибка выполнения:\n" + error);
        ui->outputInfo->repaint(); // Принудительно перерисовать
        QApplication::processEvents();
        return;
    }

    if (!output.isEmpty()) {
        QString result = QString::fromUtf8(output);
        ui->outputInfo->insertPlainText(result);
    } else {
        ui->outputInfo->insertPlainText("Нет данных от скрипта");
        ui->outputInfo->repaint(); // Принудительно перерисовать
        QApplication::processEvents();
    }

    file.remove();
    ui->outputInfo->insertPlainText("Парсинг завершен");
}
