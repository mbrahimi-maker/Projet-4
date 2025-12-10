import webview
import csv


def hello_world():
    webview.evaluate_js('document.getElementById("message").innerHTML = "Hello, Pywebview!"')

if __name__ == '__main__':
    
    # define html content
    



    myFile = open('Data/produit.csv')

    content="""
        <div id="message">
        <h1>Hello, World!</h1>
        <h2> This window was created <br />
        by <span style="color:red">Pywebview</span></h2>
        </div>
        """
    
    #ajout
    data_prod = []
    with open('./Data/produit.csv', 'r', newline='', encoding='utf-8') as csv_prod:
        r = csv.reader(csv_prod)

        for i, line in enumerate(r):
            if i == 0:
                data_prod.append(line)
            else:
                id = line[0]
                name = line[1]
                price = float(line[2])
                quantity = line[3]
                total = line[4]

                if(name == "banane"):
                    price += 1
            
                data_prod.append([id, name, price, quantity, total])


    with open('./Data/produit.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(csv_prod)
        writer.writerows(data_prod)



    # tableau
    content = content + "<h1>Table<h1>"

   
    
    text = myFile.readline()
    result = text.split(',')
    content = content + '<table><caption>Liste des produits</caption><thead><tr><th scope="col">'+result[1]+'</th><th scope="col">'+result[2]+'</th>'
    content = content + '<th scope="col">'+result[3]+'</th><th scope="col">'+result[4]+'</th></tr></thead><tbody>'

    text = myFile.readline()
    while text != "":
        if(result[0] != "id"):
            content = content + "<tr>"
            content = content + '<tr><th scope="row">'+result[1]+'</th><td>'+result[2]+'</td><td>'+result[3]+'</td><td>'+result[4]+'</td></tr>'
        
        text = myFile.readline()
        result = text.split(',')


content = content + """</table>"""





window = webview.create_window('Hello Pywebview', html=content)
webview.start(hello_world, window)