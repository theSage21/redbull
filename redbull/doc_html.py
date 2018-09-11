def gen_doc_html(version, api_list):
    doc_html = f'''
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style type="text/css">
        body{{margin:40px auto;
              max-width:650px; line-height:1.6;
              font-size:18px; color:#444;
              padding:0 10px}}
        h1,h2,h3{{line-height:1.2}}
        pre{{background-color: beige;
             border-radius: 5px;
             padding: 15px;
             border: 1px solid black;
            }}
    </style></head>
    <body>
        <h1>API Docs V{version}</h1>
        <p>The documentation is live and autogenerated.</p>
        <hr>
        <div id='docs'>
        </div>
        <script>
            var api_list = {str(api_list)};'''
    doc_html += '''
            for(var i=0; i < api_list.length; ++i){
                var url = api_list[i];
                var xmlhttp = new XMLHttpRequest();
                xmlhttp.open("OPTIONS", url, false);
                xmlhttp.onreadystatechange = function(){
                        if (xmlhttp.readyState == 4 && xmlhttp.status == 200){
                            var doc = document.createElement('pre');
                            doc.innerHTML = xmlhttp.responseText;
                            document.getElementById('docs').appendChild(doc);
                        }
                     }
                xmlhttp.send();
            }
        </script>
    </body>
    </html>
    '''
    return doc_html
