from app import app

app.run(host='0.0.0.0',port=5000,threaded=True,debug=True, use_reloader=True) #, ssl_context=('cert.pem', 'key.pem'))