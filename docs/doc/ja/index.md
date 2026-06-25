---
path: index
---
# QualCoderとは

QualCoderは、質的データ分析のための無料のオープンソースデスクトップソフトウェアです。

QualCoderでは、テキスト、画像、音声、動画のコーディングや、ジャーナルノートやメモの作成が可能です。コードをツリー状の分類体系で整理することができます。また、さまざまなレポートを生成でき、ほとんどのレポートはHTML、OpenDocument Text（ODT）、プレーンテキスト、またはExcelファイルとしてエクスポートできます。

QualCoderには、大規模言語モデル（LLM）を活用したAI支援機能が搭載されており、革新的な方法でデータの探索、分析、操作を支援します。AIとの対話型チャットを通じて、幅広いトピックや概念を探求し、新しいデータに親しむことができます。AI支援によるコーディングやテキスト分析を活用して、特定の側面をさらに深く掘り下げることができます。また、結果を統合・整理する必要がある段階に達した場合は、AIとの「コードチャット」で議論することができます。

!!! note "なぜQualCoderを使うのか？"
    - **QualCoderは無料です**。多くの定性分析ソフトウェアは、高額な一括料金や月額サブスクリプションを必要とします。
    - **QualCoderは使いやすいです**。他のソフトウェアに見られるような複雑なインターフェースがなく、定性分析を行うために必要な機能がすべて備わっています。
    - **QualCoderはオフラインでも動作します**。インターネットが常に利用できるとは限りませんが、QualCoderは動作にインターネットを必要としません。
    - **QualCoderは特定のコンピュータに縛られません**。職場が変わっても、以前の職場のライセンスに縛られたり、新しいライセンスを購入したりする心配はありません。QualCoderのライセンスがあれば、どこで作業しても、どのコンピュータにインストールされていても、ソフトウェアを使用できます。
    - **QualCoderはマルチプラットフォーム対応です**。Linux、Windows、macOSで動作するため、OSを変更しても心配する必要がなく、異なるプラットフォームを使用する同僚との共同作業も可能です。注を参照してください。
    - **QualCoderはコミュニティに支えられています**。不具合を発見した場合や、機能要望、フィードバックがある場合は、[GitHub上のQualCoderページ](https://github.com/ccbogel/QualCoder)に投稿してください。
    - **QualCoderは常に改善されています**。QualCoderは活発に開発が進められており、より新しく改良されたバージョンがリリースされています。
    - **QualCoderはオープンスタンダードに対応しています**。QualCoderは[REFI-QDA標準](https://www.qdasoftware.org/)への対応を目指しており、同僚がQualCoderを使用していなくても、そのソフトウェアがREFI-QDA標準に対応していれば、コードブックやプロジェクトを交換することができます。つまり、データが利用できなくなるリスクはありません。REFI-QDAプロジェクトとの互換性は、現時点では100％保証されているわけではありません。特に音声・動画のエクスポートおよびインポート、ならびに相対パスでリンクされたファイルについては、さらなるテストが必要です。
    - **QualCoderはカスタマイズ可能です**。変更内容をすべての人に公開する限り、QualCoderを自分のニーズに合わせて変更・適応させることができます。これは、ソフトウェアをコピーして同僚や学生に無料で提供することも可能であることを意味します。
    - **QualCoderは、オープンサイエンスを支援するソフトウェアの選択肢の一つです**。[オープンサイエンスに関するユネスコの勧告](https://www.unesco.org/en/open-science?hub=686)
    
## 現在のリリース
ソフトウェアのリリースは [Github](https://github.com/ccbogel/QualCoder/releases) から入手できます。これにはソースコードと実行ファイルが含まれています。実行ファイルを使用すれば QualCoder を簡単に実行できます（ダブルクリックで起動）。ただし、起動までに最大 20 秒かかる場合がある点にご注意ください。


[:octicons-archive-24: GitHubで入手可能なQualCoderの最新リリース（3.8.2）](/latest){ .md-button .md-button--primary }

[:fontawesome-brands-windows: QualCoder_3.8.2 Windows 11 インストーラー](/latest-windows){ .md-button .md-button--primary }

[:fontawesome-brands-windows: QualCoder_3.8.2 Windows 11 ポータブル版（ソフトウェア全体が1つのファイルに収められており、起動に時間がかかります）](/latest-windows-portable){ .md-button .md-button--primary }

[:material-apple: QualCoder_3.8.2 macOS arm64](/latest-mac){ .md-button .md-button--primary }

[:material-linux: QualCoder_3.8.2_Ubuntu](/latest-linux){ .md-button .md-button--primary }

## QualCoder をサポートする

QualCoderを気に入っていただき、お仕事に役立った場合は、[Saashub](https://www.saashub.com/qualcoder-alternatives) や [AlternativeTo](https://alternativeto.net/software/qualcoder) などのサイトでレビューを投稿していただけると幸いです。

QualCoderを大変気に入っていただいた場合や、独自の活用方法を見つけた場合は、QualCoderに関する記事をご執筆ください。

このソフトウェアは、無料でご利用いただけるよう、数え切れないほどの時間を費やして開発されました。**QualCoderをご利用いただき、気に入っていただけた場合は、開発へのご支援をお願いいたします。**

<a href="https://www.buymeacoffee.com/ccbogelB" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

QualCoderはPythonで記述されており、グラフィカルインターフェースにはQt6が使用されています。QualCoderは、Windows 11、macOS、およびUbuntu、Lubuntu、ZorinOS、Arch、FedoraなどのさまざまなLinuxディストリビューションで動作確認されています。

## ライセンス

QualCoderはLGPL v3ライセンスの下で提供されています。
