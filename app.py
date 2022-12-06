from flask import Flask, request, jsonify
from flask_caching import Cache  
from datetime import datetime
import redis
from ipynb.fs.full.lightfm import recommend_by_user
import pickle 
from utils import OpenDotaAPI, validate
import pyarrow as pa

context = pa.default_serialization_context()
conn = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)
r = redis.Redis(host='localhost', port=6379, db=0)


app = Flask(__name__)
app.config.from_object('config.Config') 
cache = Cache(app)  # Initialize Cache
dotaApi = OpenDotaAPI()

# Return wins and losses for a given player id
@app.route("/players", methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def get_player_leaderboard():
    player_ids = request.args.getlist('player_id')
    print(f"player id: {player_ids}")
    date_string  = request.args.get('date', default=None, type=str)
    print(f"type date string {type(date_string)} {date_string}")
    if date_string !=None:
        if date_string  =='last_week':
            days = 7 
        elif date_string =='last_month':
            days = 30 
        elif date_string  == 'last_year':
            days=365
        else:
            days=None
    
        if validate(date_string):
            someday = datetime.strptime(date_string,  '%Y-%m-%d').date()
            today = datetime.today().date()
            days = (today - someday).days
    result = []
    if date_string:
        params = {'date': days}
    else:
        params = None
    for player_id in player_ids:  
        print(f"player id :{player_id}")  
        url = "https://api.opendota.com/api/players/{}/wl".format(player_id)
        resp = dotaApi._call(url, params)
        if "error" not in resp:
            print(f"got the response from dotaapi {resp}")
            if (resp["win"] +resp["lose"]) !=0:
                win_rate =  round(resp['win'] / (resp["win"] +resp["lose"]),2)
            else: 
                win_rate = 0 
            single_player = {"player_id":player_id,"win_rate":win_rate}
        else:
            single_player = {"player_id":player_id,"win_rate":0}
        result.append(single_player)
    print(f"result {result}")
    return jsonify(result)

@app.route("/recommend_hero", methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def recommend_hero():
    player_id = request.args.get('player_id',type=int)
    print(f"player id :{player_id}, type: {type(player_id)}")  
    modelfile = 'models/lighfm.pickle'
    model = pickle.load(open(modelfile, 'rb'))
    interactions = context.deserialize(r.get("interactions"))
    user_dict_permuted = r.hgetall('user_dict_permuted')
    user_dict = {int(k):int(v) for k,v in user_dict_permuted.items()}

    hero_dict_permuted = r.hgetall('hero_dict_permuted')
    hero_dict = {int(k):str(v.decode('utf-8')) for k,v in hero_dict_permuted.items()}

    if r.hget("user_dict_permuted", str(player_id)):
        print("i am using lightfm")
        #TODO call lightfm 
        recommendations = recommend_by_user(model = model, 
                                      interactions = interactions, 
                                      user_id = player_id, 
                                      user_dict = user_dict,
                                      item_dict = hero_dict, 
                                      threshold = 0,
                                      nrec_items = 1,
                                      show = False)
    else:
        #recommend the most popular hero 
        hero_id = interactions.apply(lambda x: x.argmax(), axis=1).iloc[0]
        recommendations = [{"hero_id":str(hero_id), "name":hero_dict[hero_id]}]
   
    print(recommendations)
    return jsonify(recommendations)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)