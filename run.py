from app import create_app, db  

# Создаем экземпляр приложения  
app = create_app()  
 

if __name__ == '__main__': 
    with app.app_context():  
        db.create_all()
    # Запускаем приложение для разработки  
    app.run(host="0.0.0.0", port=5000, debug=True)
