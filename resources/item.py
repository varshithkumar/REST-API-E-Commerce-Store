from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
import sqlite3
from models.item import ItemModel

class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price',
    type=float,
    required=True,
    help="This field cannot be left blank!")

    parser = reqparse.RequestParser()
    parser.add_argument('store_id',
    type=int,
    required=True,
    help="Every item needs a store id")

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message':'item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)},400
        """ We take the data only after we check if the item is in the datalist or not
        then we take the reqparse data"""
        data = Item.parser.parse_args()
        item = ItemModel(name, data['price'], data['store_id'])
        try:
            item.save_to_db()
        except:
            return {"message":"An error occurred inserting the item"}, 500 #internal server error
        return item.json(), 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        return {"message":"item deleted"}

    def put(self, name):
        #Since PUT is idempotent we don't need to check if the item is in the datalist
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, data['price'], data['store_id'])
        else:
            item.price = data['price']
        item.save_to_db()

        return item.json()


class ItemList(Resource) :
    def get(self):
        return {'items':list(map(lambda x: x.json(), ItemModel.query.all()))}
