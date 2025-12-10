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
    r = csv.reader(myFile)
    lines = list(r)
    
    if lines[2][1] != "":
        lines[2][1] = '30'


    with open('Data/produit.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(myFile)
        writer.writerows(lines)


    # tableau
    content = content + "<h1>Table<h1>"

   

    text = myFile.readline()
    content = content + '<table><caption>Liste des produits</caption><thead><tr><th scope="col">'+result[1]+'</th><th scope="col">'+result[1]+'</th>'
    content = content + '<th scope="col">'+result[1]+'</th><th scope="col">'+result[1]+'</th></tr></thead><tbody>'
    while text != "":
        content = content + "<tr>"
        content = content + '<tr><th scope="row">'+result[1]+'</th><td>'+result[2]+'</td><td>'+result[3]+'</td><td>'+result[4]+'</td></tr>'
        text = myFile.readline()
        result = text.split(',')


content = content + """</table>"""





window = webview.create_window('Hello Pywebview', html=content)
webview.start(hello_world, window)