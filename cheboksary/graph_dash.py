import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import pandas as pd

def get_data_from_df(df):
    lat = list(df['latitude'])
    lon = list(df['longitude'])
    addr = list(df['full_address'])
    return lat, lon, addr, categ

compare_dict = {
    'зелёные насаждения': ['роща', 'дуб', 'кедр', 'клумба', 'ландшафт', 'берёза', 'лесопосадка',
                           'сирень', 'куст', 'ель', 'ёлочка', 'газон', 'клён', 'жасмина', 'цветок',
                           'рябина', 'посадка', 'зелень', 'полесадник', 'полисадник', 'озеленение',
                           'дубрава', 'дерьево', 'палисадник', 'растение', 'лесопарк', 'кустарник',
                           'лес', 'насаждение', 'питомец', 'цветник', 'озелениния', 'дерево', 'флора',
                           'пустырь', 'трава', 'заповедник', 'выгул', 'выгуливание', ],
    'асфальтовая дорожка': ['тротуар', 'дорога', 'бордюр','тратуар', 'дрога', 'асфальтирование',
                            'освальт', 'дорги', 'асвальт', 'асфальт', 'асфалта', 'кочка', 'ям',
                            'лужа', 'пандус', 'мост', 'бардюр', 'ямка', 'щебёнка', 'ухаб',
                            'сьезд', 'холм', 'подход', 'горка', 'переход', 'брусчатка', 'автодорога',
                            'выбоина', 'ливневка', 'отмосток', 'отмостка', 'обочина', 'песок', 'пандус',
                            'колесо', 'езда', 'бетон', 'зазор', 'дублёр', 'подъём', 'заезд', 'плитка', 'выезд',
                            'вьезд', 'вьезда', 'поворот', 'автомобиль', 'ходьба', ],
    'спортивная площадка': ['футбол', 'тренажёрка', 'баскетбол', 'спортивень', 'спорткомплекс',
                            'спортзал', 'спортинвентарь', 'спортплощадка', 'спортивна', 'фитнес',
                            'скейтпарк', 'скейтборд', 'спортцентр', 'каток', 'спорт', 'тренажёр', 'самокат',
                            'пеннибордовый', 'поле', ],
    'общественный туалет': ['туалет', 'санузел', ],
    'лавочка': ['скомейка', 'скамёк', 'лавочка', 'присесть', 'скаммейка', 'поставитьскомейка', 'лавка', 'скамейка', ],
    'освещение': ['светильник', 'освещение', 'фанари', 'темнота', 'свет', ],
    'беседка': ['беседка', ],
    'детский городок': ['городок', 'песочница', ],
    'навигация': ['знак', 'информаца', 'инф', ],
    'игровая площадка': ['мяч', 'игра', 'карусель', ' качель', 'скейтпарка', 'теннис', 'кочель', 'качели', ],
    'летний открытый кинотеатр': ['кинотеатр', 'сцена', ],
    'благоустройство': ['благоустройство', 'благоустроиство', 'благоустроитство', 'блогоустроиства',
                        'благоуствойство', 'благоустоиство', ' благоустроство', ' облагораживание',
                        'благоустройсть', 'улучшение', 'благоустроитва', 'реставрация', 'обустройство',
                        'мемориал', 'обелиск', 'преобразить', 'набережная', 'река', 'пляж', 'берег', 'водоём',
                        'ручей', 'речка', 'фонтан', 'парковка', 'стоянка', 'экопарковка', 'светафора', ],
    'парк': ['сквер', 'аллея', 'парк', ],
    'велосипедная дорожка': ['велодорожка', 'велосипедист', 'велосипед', 'велопрогулка', ],
    'место тихого отдыха': ['прогулка', 'бульвар', ],
    'беговая дорожка': ['бег', 'дорожка, '],
    'другое': ['ресторан', 'двор', 'стадион', 'рлощадка', 'площадк', 'плошадка', 'площака', 'развлечение',
               'полщадка', 'зона', 'площудка', 'плащадка', 'оращение', 'площадка', 'супермаркет', 'музей',
               'благосостояние', 'поляна', 'кафе', 'парковый', 'ролик', ]
}

mapbox_access_token = 'pk.eyJ1IjoiZGdyaWIiLCJhIjoiY2t2Y2loZm9jNGtoazJ1cXdhMjNzcWw1dCJ9.-xV9gvuA19QBRqbPARFdWA'

df_list = []

for i in range(len(compare_dict)):
    df_list.append(pd.read_csv(f'geodata/geodata{i}.csv'))


app = Dash(__name__)
app.layout = html.Div([
    html.H1("Карта потребностей жителей г.Чебоксары", style={'text-align': 'center'}),
dcc.Dropdown(id="slct_facility",
                 options=[
                     {"label": "toilet", "value": "туалет"},
                     {"label": "park", "value": 'парк'},
                     {"label": "asfalt", "value": "асфальт"},],
                 multi=True,
                 value="туалет",
                 style={'width': "100%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_map', figure={})

])

categ = list(compare_dict.keys())

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_map', component_property='figure')],
    [Input(component_id='slct_facility', component_property='value')]
)
def update_graph(option_slctd):
    option_slctd="парк"
    container = "The year chosen by user was: {}".format(option_slctd)

    fig = go.Figure()

    # Add first scatter trace with medium sized markers
    for i, df_temp in enumerate(df_list):
        lat, lon, addr, categ = get_data_from_df(df_temp)
        name = categ[i]

        fig.add_trace(go.Scattermapbox(
            lon=lon, lat=lat, text=addr, name=name))

    fig.update_layout(
        mapbox={
            'center': go.layout.mapbox.Center(lat=56.1163, lon=47.2603),
            'accesstoken': mapbox_access_token,
            'style': "outdoors", 'zoom': 11},
        width=1200,
        height=800,
        showlegend=True),


    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, host="localhost", port=8051)

