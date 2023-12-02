import requests
import dash
from dash import Dash, Input, Output, html, dcc, ctx, no_update, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
import os


# Ajoute le thème Bootstrap pour l'apparence
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.SPACELAB])

nom_user = "chatvoyou"
user_id = 0

app.layout = html.Div(style={'backgroundColor': '#EDF8F8'}, children=[
    
    html.Img(src='https://www.not-only-books.fr/wp-content/uploads/2023/02/livres-realisation-creation-externalisation-edition-812x1024.png',style={'width': '40px', 'float': 'left'}),

    html.H1(children=" BiblioTech", style={'color': '#01756C', "font-weight": "bold"}),

    html.H3(children=f" Bienvenue {nom_user} !", style={'color': '#01756C', 'display': 'inline-block', 'margin-left': '20px'}),

    
    html.Div(style={'margin': '20px'}),

    # DataTable pour afficher tous les livres
    #html.Button("Ajouter des livres à ma liste de lecture", id="bouton_recherche", n_clicks=0),

    html.Div(style={'margin': '20px'}),

    # Add the dummy input component
    dcc.Input(id='dummy-input', value='', style={'display': 'none'}),

    dash_table.DataTable(
        id='table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Titre', 'id': 'title'},
            {'name': 'Auteur', 'id': 'authors'},
            # Ajoute d'autres colonnes en fonction de tes besoins
        ],
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={
                'backgroundColor': '#01756C',
                'color': 'white',
                'fontSize': '13px',
                'textAlign': 'left'
            },
        style_header={'backgroundColor': '#01756C'},

        style_filter={
            'backgroundColor': '#EDF8F8',
        },

        style_data_conditional=[
        {
            'if': {'state': 'selected'},
            'backgroundColor': '#01756C',
            'color': '#3C3C3C',
            'border': '1px solid #01756C',  # Bordure colorée
            'textAlign': 'left',  # Aligner le texte à gauche
        }
        ],
    ),

    
    html.Div(style={'margin': '20px'}),

    # DataTable pour afficher les favoris
    dash_table.DataTable(
        id='favorites-table',
        columns=[
            {'name': 'ID', 'id': 'id'},
            {'name': 'Titre', 'id': 'title'},
            {'name': 'Auteur', 'id': 'authors'},
        ],
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_deletable=True,
        column_selectable="single",
        #row_selectable="multi",
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_cell={
                'backgroundColor': '#01756C',
                'color': 'white',
                'fontSize': '13px',
                'textAlign': 'left'
            },

        style_filter={
            'backgroundColor': '#EDF8F8',
        },
        style_data_conditional=[
        {
            'if': {'state': 'selected'},
            'backgroundColor': '#01756C',
            'color': '#3C3C3C',
            'border': '1px solid #01756C',  # Bordure colorée
            'textAlign': 'left',  # Aligner le texte à gauche
        }
        ],
    ),

    dbc.Modal(
            [
                dbc.ModalHeader("Vous avez ajouté un livre à votre liste de lecture"),
                dbc.ModalBody(id="modal-content"),
                dbc.ModalFooter(dbc.Button("Fermer", id="close", className="ml-auto", color="success")),
            ],
            id="modal",
    ),
    
])



@app.callback(
    Output("modal", "is_open"),
    Output("modal-content", "children"),
    Input('table', 'selected_rows'),
    Input("close", "n_clicks"),
)
def open_modal(selected_rows, _):
    if ctx.triggered_id == "close":
        return False, no_update
    if selected_rows:
        last_selected_row = selected_rows[-1]
        selected_book = books_data[last_selected_row]
        title = selected_book.get("title", "Unknown Title")
        return True, f"{title}"

    return no_update, no_update

@app.callback(
    # Output('table', 'data'),
    # Input("bouton_recherche", "n_clicks"),  
    # prevent_initial_call=True
    Output('table', 'data'),
    Input('dummy-input', 'value'),
    prevent_initial_call=False
)

def get_all_books_table(n):
    max_retries = 3
    retries = 0

    global books_data  # Utilise la variable globale
    # r = requests.get("http://api:5000/all_books")
    # books_data = r.json()

    while retries < max_retries:
        try:
            r = requests.get("http://api:5000/all_books")
            r.raise_for_status()
            books_data = r.json()
            # Process the data as needed
            return books_data
        except requests.exceptions.RequestException:
            retries += 1

    return []

@app.callback(
    Output('favorites-table', 'data'),
    Input('table', 'selected_rows'),
    prevent_initial_call=True
)

def update_favorites(selected_rows):
    #global books_data  # Utilise la variable globale

    if not selected_rows:
        return dash.no_update

    selected_books = [books_data[i] for i in selected_rows]

    for book in selected_books:
        usersbook = {
            "book_id": book["id"],
            "user_id": user_id
        }

        r = requests.post("http://api:5000/save_book/", json=usersbook)

        if r.status_code == 409:
            print(f"Book {book['title']} already exists in the user's favorites.")

    r = requests.get(f"http://api:5000/users_books/{user_id}")
    return r.json()



# @app.callback(
#     Output('favorites-table', 'data'),
#     Input('favorites-table', 'data_previous'),
#     prevent_initial_call=False,
# )
# def delete_book_row(data_previous):
#     if data_previous:
#         deleted_row_index = find_deleted_row_index(data_previous, dash.callback_context.triggered_id)
#         if deleted_row_index is not None:
#             delete_book_from_usersbooks(data_previous[deleted_row_index])
#             data_previous.pop(deleted_row_index)
#             return data_previous
#     return []

# def find_deleted_row_index(data_previous, triggered_id):
#     for i, row in enumerate(data_previous):
#         if f"{app.callback_context.component_id}.children" in triggered_id:
#             return i
#     return None

# def delete_book_from_usersbooks(deleted_row_data):
#     # Extract book ID from the row data and use it to delete the book from the usersbooks
#     book_id = deleted_row_data.get("id")
#     if book_id is not None:
#         # Make a request to the API or use your database deletion logic
#         usersbook_id = str(book_id) + "_" + str(user_id)  
#         requests.delete(f"http://api:5000/unfav_book/{usersbook_id}")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)