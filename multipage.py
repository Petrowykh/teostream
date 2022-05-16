import streamlit as st


class MultiPage: 
    
    def __init__(self) -> None:
        self.apps = []
    
    def add_page(self, title, func) -> None: 
        self.apps.append({
            "title": title, 
            "function": func
            })

    def run(self):
        
        app = st.selectbox(
            'Выберите раздел', 
            self.apps, 
            format_func=lambda app: app['title']
        )

        # run the app function 
        app['function']()
        #app.empty()
        
        
        