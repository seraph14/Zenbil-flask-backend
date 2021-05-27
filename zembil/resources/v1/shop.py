from flask import request
from flask_restful import Resource, abort
from flask_jwt_extended import ( jwt_required, get_jwt_identity)
from marshmallow import ValidationError
from zembil import db
from zembil.models import UserModel, ShopModel, CategoryModel
from zembil.schemas import ShopSchema
from zembil.common.util import cleanNullTerms

shop_schema = ShopSchema()
shops_schema = ShopSchema(many=True)

class Shops(Resource):
    def get(self):
        result = ShopModel.query.all()
        return shops_schema.dump(result)

    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            args = shop_schema.load(data)
        except ValidationError as errors:
            abort(400, message=errors.messages)
        user_id = get_jwt_identity()
        user = UserModel.query.get(user_id)
        if user:
            args = cleanNullTerms(args)
            shop = ShopModel(
                user_id=user_id, 
                **args)
            db.session.add(shop)
            db.session.commit()
            return shop_schema.dump(shop), 201
        abort(404, message="User Doesn't Exist")


class Shop(Resource):
    def get(self, id):
        result = ShopModel.query.filter_by(id=id).first()
        if result:
            return shop_schema.dump(result)
        abort(404, message="Shop Doesn't Exist")
    
    @jwt_required()
    def patch(self, id):
        data = request.get_json()
        try:
            args = ShopSchema(partial=True).load(data)
        except ValidationError as errors:
            abort(400, message=errors.messages)
        args = cleanNullTerms(args)
        if not args:
            abort(400, message="Empty json body")
        user = get_jwt_identity()
        existing = ShopModel.query.get(id)
        if existing and user.id == existing.user_id:
            shop = ShopModel.query.filter_by(id=id).update(args)
            db.session.commit()
            query = ShopModel.query.get(id)
            return shop_schema.dump(query), 200
        if existing:
            abort(403, message="User is not owner of this shop")
        abort(404, message="Shop doesn't exist!")

class SearchShop(Resource):
    def get(self):
        name = request.args.get('name')
        category = request.args.get('category')
        shops = ShopModel.query
        if name:
            shops = shops.filter(ShopModel.name.ilike('%' + name + '%'))
        if category:
            shops = shops.filter(CategoryModel.name.ilike('%' + category + '%'))
        shops = shops.order_by(ShopModel.name).all()
        if shops:
            return products_schema.dump(products)
        abort(404, message="Product doesn't exist!")