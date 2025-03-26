import tkinter as tk
from tkinter import messagebox, ttk
import requests
import sqlite3
from io import BytesIO
from PIL import Image, ImageTk
from googletrans import Translator
from threading import Thread

class ChefAI:
    def __init__(self, root):
        self.root = root
        self.root.title("ChefAI - Intelligent Culinary Assistant")
        self.root.geometry("1100x800")
        
        # Configuration
        self.current_language = "en"
        self.dark_mode = False
        self.current_recipe = None
        self.current_api = "themealdb"  # 'themealdb' ou 'edamam'
        self.favorites_db = "favorites.db"
        self.translator = Translator()
        self.translation_cache = {}
        
        # Clés API (à remplacer par vos propres clés)
        self.api_keys = {
            "edamam": {
                "app_id": "YOUR_EDAMAM_APP_ID",
                "app_key": "YOUR_EDAMAM_APP_KEY"
            }
        }
        
        # Thèmes
        self.themes = {
            "light": {
                "primary": "#4a6baf",
                "secondary": "#6c757d",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "bg": "#f8f9fa",
                "text": "#212529",
                "widget_bg": "#ffffff",
                "listbox_bg": "#ffffff",
                "listbox_fg": "#212529",
                "select_bg": "#4a6baf",
                "select_fg": "white"
            },
            "dark": {
                "primary": "#6c8cd5",
                "secondary": "#5a6268",
                "success": "#48a868",
                "danger": "#e4606d",
                "warning": "#ffd351",
                "bg": "#2d2d2d",
                "text": "#e0e0e0",
                "widget_bg": "#3d3d3d",
                "listbox_bg": "#3d3d3d",
                "listbox_fg": "#e0e0e0",
                "select_bg": "#6c8cd5",
                "select_fg": "white"
            }
        }
        
        # Textes bilingues
        self.texts = {
            "en": {
                "search": "Recipe Search",
                "search_btn": "Search",
                "placeholder": "Enter recipe name...",
                "ingredients": "Ingredients",
                "instructions": "Instructions",
                "translate": "Translate to French",
                "save": "Save to Favorites",
                "no_results": "No recipes found",
                "search_error": "Please enter a search term",
                "save_success": "Recipe saved!",
                "trans_error": "Translation failed",
                "api_error": "API request failed",
                "title": "ChefAI - Intelligent Culinary Assistant",
                "dark_mode": "Dark Mode",
                "light_mode": "Light Mode",
                "api_select": "API Source:",
                "themealdb": "TheMealDB",
                "edamam": "Edamam"
            },
            "fr": {
                "search": "Recherche de Recettes",
                "search_btn": "Rechercher",
                "placeholder": "Entrez le nom d'une recette...",
                "ingredients": "Ingrédients",
                "instructions": "Instructions",
                "translate": "Traduire en Français",
                "save": "Sauvegarder",
                "no_results": "Aucune recette trouvée",
                "search_error": "Veuillez entrer un terme de recherche",
                "save_success": "Recette sauvegardée !",
                "trans_error": "Échec de traduction",
                "api_error": "Échec de la requête API",
                "title": "ChefAI - Assistant Culinaire Intelligent",
                "dark_mode": "Mode Sombre",
                "light_mode": "Mode Clair",
                "api_select": "Source API :",
                "themealdb": "TheMealDB",
                "edamam": "Edamam"
            }
        }
        
        # Initialisation
        self.init_database()
        self.configure_styles()
        self.create_widgets()
        self.update_ui()
    
    def init_database(self):
        """Initialise la base de données SQLite"""
        conn = sqlite3.connect(self.favorites_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS favorites
                    (id TEXT PRIMARY KEY, 
                     title TEXT, 
                     ingredients TEXT, 
                     instructions TEXT,
                     image_url TEXT,
                     source TEXT)''')
        conn.commit()
        conn.close()
    
    def configure_styles(self):
        """Configure les styles ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        current_theme = "dark" if self.dark_mode else "light"
        colors = self.themes[current_theme]
        
        style.configure('.', background=colors["bg"])
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["text"])
        style.configure('TButton', padding=8, font=('Helvetica', 10, 'bold'))
        style.configure('TEntry', padding=8, fieldbackground=colors["widget_bg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["primary"])
        style.configure('TLabelframe.Label', background=colors["bg"], foreground=colors["primary"])
        style.configure('TNotebook', background=colors["bg"])
        style.configure('TNotebook.Tab', background=colors["bg"], padding=[10, 5], foreground=colors["text"])
        style.configure('TRadiobutton', background=colors["bg"], foreground=colors["text"])
        
        # Styles pour les boutons
        style.configure('Primary.TButton', 
                      foreground='white',
                      background=colors["primary"],
                      borderwidth=1)
        style.map('Primary.TButton',
                 foreground=[('active', 'white')],
                 background=[('active', colors["primary"])])
        
        style.configure('Secondary.TButton', 
                       foreground=colors["text"],
                       background=colors["bg"],
                       borderwidth=1)
        style.map('Secondary.TButton',
                 foreground=[('active', 'white')],
                 background=[('active', colors["secondary"])])
        
        style.configure('Success.TButton', 
                       foreground='white',
                       background=colors["success"],
                       borderwidth=1)
        style.map('Success.TButton',
                 foreground=[('active', 'white')],
                 background=[('active', colors["success"])])
    
    def create_widgets(self):
        """Crée l'interface utilisateur"""
        # Barre d'outils
        toolbar_frame = ttk.Frame(self.root, padding=(10, 5))
        toolbar_frame.pack(fill=tk.X)
        
        # Bouton de mode sombre/clair
        self.theme_btn = ttk.Button(
            toolbar_frame, 
            text=self.texts[self.current_language]["dark_mode"] if not self.dark_mode else self.texts[self.current_language]["light_mode"],
            command=self.toggle_theme,
            style='Secondary.TButton'
        )
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
        # Sélection d'API
        api_frame = ttk.Frame(toolbar_frame)
        api_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(api_frame, text=self.texts[self.current_language]["api_select"]).pack(side=tk.LEFT)
        
        self.api_var = tk.StringVar(value=self.current_api)
        ttk.Radiobutton(
            api_frame, 
            text=self.texts[self.current_language]["themealdb"],
            variable=self.api_var, 
            value="themealdb",
            command=self.change_api
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            api_frame, 
            text=self.texts[self.current_language]["edamam"],
            variable=self.api_var, 
            value="edamam",
            command=self.change_api
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton de langue
        self.lang_btn = ttk.Button(
            toolbar_frame, 
            text="FR/EN", 
            command=self.toggle_language, 
            style='Secondary.TButton'
        )
        self.lang_btn.pack(side=tk.RIGHT, padx=5)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Zone de recherche
        self.search_frame = ttk.LabelFrame(main_frame, text=self.texts[self.current_language]["search"])
        self.search_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.search_entry = ttk.Entry(self.search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.search_entry.insert(0, self.texts[self.current_language]["placeholder"])
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == self.texts[self.current_language]["placeholder"] else None)
        
        self.search_btn = ttk.Button(
            self.search_frame, 
            text=self.texts[self.current_language]["search_btn"], 
            command=self.search_recipes, 
            style='Primary.TButton'
        )
        self.search_btn.pack(side=tk.LEFT)
        
        # Liste des résultats
        current_theme = "dark" if self.dark_mode else "light"
        colors = self.themes[current_theme]
        
        self.recipes_list = tk.Listbox(
            main_frame, 
            height=10, 
            bg=colors["listbox_bg"], 
            fg=colors["listbox_fg"], 
            font=('Helvetica', 11), 
            selectbackground=colors["select_bg"],
            selectforeground=colors["select_fg"]
        )
        self.recipes_list.pack(fill=tk.BOTH, pady=5, expand=True, padx=5)
        self.recipes_list.bind('<<ListboxSelect>>', self.show_recipe_details)
        
        # Détails de la recette
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image
        self.recipe_image = ttk.Label(details_frame)
        self.recipe_image.pack(pady=5)
        
        # Titre et boutons
        title_frame = ttk.Frame(details_frame)
        title_frame.pack(fill=tk.X, pady=5)
        
        self.recipe_title = ttk.Label(
            title_frame, 
            font=('Helvetica', 16, 'bold'), 
            foreground=self.themes["dark" if self.dark_mode else "light"]["primary"]
        )
        self.recipe_title.pack(side=tk.LEFT, padx=5)
        
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        self.translate_btn = ttk.Button(
            btn_frame, 
            text=self.texts[self.current_language]["translate"], 
            command=self.translate_recipe, 
            style='Secondary.TButton'
        )
        self.translate_btn.pack(side=tk.LEFT, padx=2)
        
        self.save_btn = ttk.Button(
            btn_frame, 
            text=self.texts[self.current_language]["save"], 
            command=self.save_to_favorites, 
            style='Success.TButton'
        )
        self.save_btn.pack(side=tk.LEFT)
        
        # Onglets
        self.notebook = ttk.Notebook(details_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet Ingrédients
        ingredients_frame = ttk.Frame(self.notebook)
        self.ingredients_text = tk.Text(
            ingredients_frame, 
            wrap=tk.WORD, 
            bg=colors["widget_bg"], 
            fg=colors["text"], 
            font=('Helvetica', 11), 
            padx=10, 
            pady=10,
            insertbackground=colors["text"]
        )
        scroll_ing = ttk.Scrollbar(ingredients_frame, command=self.ingredients_text.yview)
        self.ingredients_text.configure(yscrollcommand=scroll_ing.set)
        scroll_ing.pack(side=tk.RIGHT, fill=tk.Y)
        self.ingredients_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(ingredients_frame, text=self.texts[self.current_language]["ingredients"])
        
        # Onglet Instructions
        instructions_frame = ttk.Frame(self.notebook)
        self.instructions_text = tk.Text(
            instructions_frame, 
            wrap=tk.WORD, 
            bg=colors["widget_bg"], 
            fg=colors["text"], 
            font=('Helvetica', 11), 
            padx=10, 
            pady=10,
            insertbackground=colors["text"]
        )
        scroll_inst = ttk.Scrollbar(instructions_frame, command=self.instructions_text.yview)
        self.instructions_text.configure(yscrollcommand=scroll_inst.set)
        scroll_inst.pack(side=tk.RIGHT, fill=tk.Y)
        self.instructions_text.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(instructions_frame, text=self.texts[self.current_language]["instructions"])
    
    def change_api(self):
        """Change l'API source"""
        self.current_api = self.api_var.get()
        self.recipes_list.delete(0, tk.END)
        self.clear_recipe_details()
    
    def clear_recipe_details(self):
        """Efface les détails de la recette actuelle"""
        self.recipe_title.config(text="")
        self.recipe_image.config(image="")
        self.recipe_image.image = None
        self.ingredients_text.config(state=tk.NORMAL)
        self.ingredients_text.delete(1.0, tk.END)
        self.ingredients_text.config(state=tk.DISABLED)
        self.instructions_text.config(state=tk.NORMAL)
        self.instructions_text.delete(1.0, tk.END)
        self.instructions_text.config(state=tk.DISABLED)
        self.current_recipe = None
    
    def toggle_theme(self):
        """Bascule entre le mode sombre et clair"""
        self.dark_mode = not self.dark_mode
        self.update_ui()
    
    def toggle_language(self):
        """Change la langue de l'interface"""
        self.current_language = "fr" if self.current_language == "en" else "en"
        self.update_ui()
    
    def update_ui(self):
        """Met à jour toute l'interface"""
        self.configure_styles()
        current_theme = "dark" if self.dark_mode else "light"
        colors = self.themes[current_theme]
        
        self.root.configure(bg=colors["bg"])
        
        # Mise à jour des widgets
        self.recipes_list.config(
            bg=colors["listbox_bg"],
            fg=colors["listbox_fg"],
            selectbackground=colors["select_bg"],
            selectforeground=colors["select_fg"]
        )
        
        for widget in [self.ingredients_text, self.instructions_text]:
            widget.config(
                bg=colors["widget_bg"],
                fg=colors["text"],
                insertbackground=colors["text"]
            )
        
        self.recipe_title.config(foreground=colors["primary"])
        self.theme_btn.config(
            text=self.texts[self.current_language]["light_mode"] if self.dark_mode else self.texts[self.current_language]["dark_mode"]
        )
        
        # Textes de l'interface
        self.root.title(self.texts[self.current_language]["title"])
        self.search_frame.config(text=self.texts[self.current_language]["search"])
        self.search_btn.config(text=self.texts[self.current_language]["search_btn"])
        self.translate_btn.config(text="Translate to French" if self.current_language == "en" else "Traduire en Français")
        self.save_btn.config(text=self.texts[self.current_language]["save"])
        self.notebook.tab(0, text=self.texts[self.current_language]["ingredients"])
        self.notebook.tab(1, text=self.texts[self.current_language]["instructions"])
        
        # Placeholder
        current_text = self.search_entry.get()
        if current_text in [v["placeholder"] for v in self.texts.values()]:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self.texts[self.current_language]["placeholder"])
    
    def search_recipes(self):
        """Recherche des recettes selon l'API sélectionnée"""
        query = self.search_entry.get().strip()
        if not query or query == self.texts[self.current_language]["placeholder"]:
            messagebox.showwarning(
                self.texts[self.current_language]["search_error"], 
                self.texts[self.current_language]["search_error"]
            )
            return
        
        if self.current_api == "themealdb":
            self.search_themealdb(query)
        else:
            self.search_edamam(query)
    
    def search_themealdb(self, query):
        """Recherche sur TheMealDB API"""
        try:
            response = requests.get(
                "https://www.themealdb.com/api/json/v1/1/search.php",
                params={"s": query},
                timeout=10
            )
            data = response.json()
            
            if not data.get("meals"):
                messagebox.showinfo(
                    self.texts[self.current_language]["no_results"], 
                    self.texts[self.current_language]["no_results"]
                )
                return
            
            self.recipes = []
            for meal in data["meals"]:
                ingredients = []
                for i in range(1, 21):
                    ingredient = meal.get(f"strIngredient{i}")
                    measure = meal.get(f"strMeasure{i}")
                    if ingredient and ingredient.strip():
                        ingredients.append(f"{measure} {ingredient}")
                
                self.recipes.append({
                    "id": meal["idMeal"],
                    "title": meal["strMeal"],
                    "ingredients": "\n".join(ingredients),
                    "instructions": meal["strInstructions"],
                    "image_url": meal["strMealThumb"],
                    "source": "themealdb"
                })
            
            self.display_recipes_list()
            
        except Exception as e:
            messagebox.showerror(
                self.texts[self.current_language]["api_error"], 
                f"{self.texts[self.current_language]['api_error']}: {str(e)}"
            )
    
    def search_edamam(self, query):
        """Recherche sur Edamam API"""
        try:
            response = requests.get(
                "https://api.edamam.com/api/recipes/v2",
                params={
                    "type": "public",
                    "q": query,
                    "app_id": self.api_keys["edamam"]["app_id"],
                    "app_key": self.api_keys["edamam"]["app_key"]
                },
                timeout=10
            )
            data = response.json()
            
            if not data.get("hits") or len(data["hits"]) == 0:
                messagebox.showinfo(
                    self.texts[self.current_language]["no_results"], 
                    self.texts[self.current_language]["no_results"]
                )
                return
            
            self.recipes = []
            for hit in data["hits"]:
                recipe = hit["recipe"]
                
                # Formater les ingrédients
                ingredients = []
                for ingredient in recipe.get("ingredients", []):
                    ingredients.append(f"{ingredient.get('quantity', '')} {ingredient.get('measure', '').lower()} {ingredient['food']}")
                
                self.recipes.append({
                    "id": recipe["uri"].split("#")[1],
                    "title": recipe["label"],
                    "ingredients": "\n".join(ingredients),
                    "instructions": "\n".join(recipe.get("instructionLines", ["No instructions available"])),
                    "image_url": recipe["image"],
                    "source": "edamam"
                })
            
            self.display_recipes_list()
            
        except Exception as e:
            messagebox.showerror(
                self.texts[self.current_language]["api_error"], 
                f"{self.texts[self.current_language]['api_error']}: {str(e)}"
            )
    
    def display_recipes_list(self):
        """Affiche la liste des recettes"""
        self.recipes_list.delete(0, tk.END)
        for recipe in self.recipes:
            self.recipes_list.insert(tk.END, recipe["title"])
    
    def show_recipe_details(self, event):
        """Affiche les détails de la recette sélectionnée"""
        selection = self.recipes_list.curselection()
        if not selection:
            return
        
        recipe = self.recipes[selection[0]]
        self.current_recipe = recipe
        self.current_language = "en"  # Reset to English when new recipe selected
        
        self.recipe_title.config(text=recipe["title"])
        self.load_image_async(recipe["image_url"])
        
        self.update_text_widgets(recipe)
    
    def load_image_async(self, url):
        """Charge l'image en arrière-plan"""
        def fetch_image():
            try:
                response = requests.get(url, stream=True, timeout=10)
                img = Image.open(BytesIO(response.content))
                img.thumbnail((350, 350))
                photo = ImageTk.PhotoImage(img)
                self.root.after(0, lambda: self.display_image(photo))
            except Exception as e:
                print(f"Image error: {e}")
        
        Thread(target=fetch_image, daemon=True).start()
    
    def display_image(self, photo):
        """Affiche l'image chargée"""
        self.recipe_image.config(image=photo)
        self.recipe_image.image = photo
    
    def update_text_widgets(self, recipe):
        """Met à jour les zones de texte"""
        for widget, content in [
            (self.ingredients_text, recipe["ingredients"]),
            (self.instructions_text, recipe["instructions"])
        ]:
            widget.config(state=tk.NORMAL)
            widget.delete(1.0, tk.END)
            widget.insert(tk.END, content)
            widget.config(state=tk.DISABLED)
    
    def translate_recipe(self):
        """Traduit la recette entre français et anglais"""
        if not self.current_recipe:
            return
        
        recipe = self.current_recipe
        target_lang = "fr" if self.current_language == "en" else "en"
        
        try:
            Thread(target=self._translate_recipe_background, args=(recipe, target_lang), daemon=True).start()
        except Exception as e:
            messagebox.showerror(
                self.texts[self.current_language]["trans_error"], 
                f"{self.texts[self.current_language]['trans_error']}: {str(e)}"
            )
    
    def _translate_recipe_background(self, recipe, target_lang):
        """Traduction en arrière-plan"""
        self.root.after(0, lambda: self.recipe_title.config(
            text="Translating..." if target_lang == "fr" else "Traduction en cours..."
        ))
        
        translated_title = self._translate_with_cache(recipe["title"], target_lang)
        ingredients = recipe["ingredients"].split("\n")
        translated_ingredients = [self._translate_with_cache(ing, target_lang) for ing in ingredients]
        translated_instructions = self._translate_with_cache(recipe["instructions"], target_lang)
        
        self.root.after(0, lambda: self._update_translated_ui(
            translated_title,
            "\n".join(translated_ingredients),
            translated_instructions,
            target_lang
        ))
    
    def _translate_with_cache(self, text, target_lang):
        """Traduction avec cache"""
        cache_key = f"{text}_{target_lang}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        translated = self.translator.translate(text, src='en' if target_lang == 'fr' else 'fr', dest=target_lang).text
        self.translation_cache[cache_key] = translated
        return translated
    
    def _update_translated_ui(self, title, ingredients, instructions, target_lang):
        """Met à jour l'interface avec la traduction"""
        self.current_language = target_lang
        self.recipe_title.config(text=title)
        self.translate_btn.config(text="Translate to French" if target_lang == "fr" else "Traduire en Anglais")
        
        for widget, content in [
            (self.ingredients_text, ingredients),
            (self.instructions_text, instructions)
        ]:
            widget.config(state=tk.NORMAL)
            widget.delete(1.0, tk.END)
            widget.insert(tk.END, content)
            widget.config(state=tk.DISABLED)
    
    def save_to_favorites(self):
        """Sauvegarde la recette en favoris"""
        if not self.current_recipe:
            return
        
        try:
            conn = sqlite3.connect(self.favorites_db)
            c = conn.cursor()
            
            c.execute('''INSERT OR IGNORE INTO favorites 
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (self.current_recipe["id"],
                      self.current_recipe["title"],
                      self.current_recipe["ingredients"],
                      self.current_recipe["instructions"],
                      self.current_recipe["image_url"],
                      self.current_recipe["source"]))
            
            conn.commit()
            messagebox.showinfo(
                self.texts[self.current_language]["save_success"], 
                self.texts[self.current_language]["save_success"]
            )
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"{self.texts[self.current_language]['save_success']}: {str(e)}"
            )
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChefAI(root)
    root.mainloop()