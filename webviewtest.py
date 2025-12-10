import webview
import csv
import os


def hello_world():
    webview.evaluate_js('document.getElementById("message").innerHTML = "Hello, Pywebview!"')


if __name__ == '__main__':
    csv_path = os.path.join(os.path.dirname(__file__), 'Data', 'produit.csv')

    # message initial
    content = """
        <div id="message">
        <h1>Hello, World!</h1>
        <h2> This window was created <br />
        by <span style="color:red">Pywebview</span></h2>
        </div>
        """

    # lecture et modification des données
    data_prod = []
    header = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as csv_prod:
        reader = csv.reader(csv_prod)
        for i, row in enumerate(reader):
            if i == 0:
                header = row
                data_prod.append(row)
            else:
                if len(row) < 5:
                    continue
                id0 = row[0]
                name = row[1]
                try:
                    price = float(row[2])
                except Exception:
                    price = 0.0
                quantity = row[3]
                total = row[4]

                if name == "banane":
                    price += 1

                data_prod.append([id0, name, f"{price}", quantity, total])

    # écriture des données modifiées (corrigé : on écrit dans le bon fichier)
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data_prod)

    # génération du tableau HTML à partir des données lues
    content += "<h1>Table</h1>"

    if header and len(header) >= 5:
        content += (
            '<table><caption>Liste des produits</caption>'
            '<thead><tr>'
            f'<th scope="col">{header[1]}</th>'
            f'<th scope="col">{header[2]}</th>'
            f'<th scope="col">{header[3]}</th>'
            f'<th scope="col">{header[4]}</th>'
            '</tr></thead><tbody>'
        )
    else:
        content += '<table><tbody>'

    for row in data_prod[1:]:
        if len(row) >= 5 and row[0] != "id":
            content += (
                '<tr>'
                f'<th scope="row">{row[1]}</th>'
                f'<td>{row[2]}</td>'
                f'<td>{row[3]}</td>'
                f'<td>{row[4]}</td>'
                '</tr>'
            )

    content += "</tbody></table>"

    window = webview.create_window('Hello Pywebview', html=content)
    webview.start(hello_world, window)