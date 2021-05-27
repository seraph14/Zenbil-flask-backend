from flask import request
from flask_restful import Resource, abort
from flask_jwt_extended import ( jwt_required, get_jwt_identity)
from marshmallow import ValidationError
from zembil import db
from zembil.models import ProductModel, ShopModel, CategoryModel
from zembil.schemas import ProductSchema, ShopProductSchema
from zembil.common.util import cleanNullTerms

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
shop_products_schema = ShopProductSchema()

class Products(Resource):
    def get(self):
        products = ProductModel.query.all()
        return products_schema.dump(products)
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            args = product_schema.load(data)
        except ValidationError as errors:
            abort(400, message=errors.messages)
        args = cleanNullTerms(args)
        user_id = get_jwt_identity()
        shop_owner = ShopModel.query.filter_by(user_id=user_id).first()
        if shop_owner and args:
            product = ProductModel(**args)
            db.session.add(product)
            db.session.commit()
            return product_schema.dump(product), 201
        abort(403, message="Shop doesn't belong to this user")
        

class Product(Resource):
    def get(self, id):
        product = ProductModel.query.filter_by(id=id).first()
        if product:
            return product_schema.dump(product)
        abort(404, message="Product doesn't exist!") 

    @jwt_required()
    def patch(self, id):
        data = request.get_json()
        try:
            args = ProductSchema(partial=True).load(data)
        except ValidationError as errors:
            abort(400, message=errors.messages)
        args = cleanNullTerms(args)
        existing = ProductModel.query.get(id)
        if existing and args:
            product = ProductModel.query.filter_by(id=id).update(args)
            db.session.commit()
            return product_schema.dump(ProductModel.query.get(id)), 200
        if not existing:
            abort(404, message="Product doesn't exist!")
        abort(400, message="Empty body was given")

class ShopProducts(Resource):
    def get(self, shop_id):
        shop = ShopModel.query.get(shop_id)
        if shop:
            return shop_products_schema.dump(shop)
        abort(404, message="Shop doesn't exist!")


class SearchProduct(Resource):
    def get(self):
        name = request.args.get('name')
        category = request.args.get('category')
        products = ProductModel.query
        if name:
            products = products.filter(ProductModel.name.ilike('%' + name + '%'))
        if category:
            products = products.filter(CategoryModel.name.ilike('%' + category + '%'))
        products = products.order_by(ProductModel.name).all()
        if products:
            return products_schema.dump(products)
        abort(404, message="Product doesn't exist!")