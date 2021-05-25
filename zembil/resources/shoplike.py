from flask_restful import Resource, fields, reqparse, abort
from flask_jwt_extended import ( jwt_required, get_jwt_identity)
from zembil import db
from zembil.models import ShopLikeModel
from zembil.schemas import ShopLikeSchema

shoplike_schema = ShopLikeSchema()
shoplikes_schema = ShopLikeSchema(many=True)

shoplike_post_arguments = reqparse.RequestParser()
shoplike_post_arguments.add_argument("shopid", type=int, help="Product Id is required", required=True)
shoplike_post_arguments.add_argument("upvoted", type=bool, required=False)
shoplike_post_arguments.add_argument("downvoted", type=bool, required=False)

shoplike_update_arguments = reqparse.RequestParser()
shoplike_update_arguments.add_argument("shopid", type=int, help="Product Id is required", required=True)
shoplike_update_arguments.add_argument("upvoted", type=bool, required=False)
shoplike_update_arguments.add_argument("downvoted", type=bool, required=False)

class ShopLike(Resource):
    def get(self):
        shoplike = ShopLikeModel.query.all()
        if shoplike:
            return shoplikes_schema.dump(shoplike)
        return abort(404, "No Shop Likes Found")
    
    @jwt_required()
    def post(self):
        args = shoplike_post_arguments.parse_args()
        user_id = get_jwt_identity()
        existing = ShopLikeModel.query.filter_by(user_id=user_id).first()
        if not existing:
            if args['downvoted']:
                shoplike = ShopLikeModel(
                    user_id=user_id,
                    shop_id=args['shopid'],
                    upvoted=False,
                    downvoted=True
                )
            elif args['upvoted']:
                shoplike = ShopLikeModel(
                    user_id=user_id,
                    shop_id=args['shopid'],
                    upvoted=True,
                    downvoted=False
                )
            else:
                shoplike = ShopLikeModel(
                    user_id=user_id,
                    shop_id=args['shopid'],
                )
            db.session.add(shoplike)
            db.session.commit()
            return shoplike_schema.dump(shoplike), 201
        return abort(409, message="User already upvoted or downvoted")

    
    @jwt_required()
    def patch(self):
        args = shoplike_update_arguments.parse_args()
        user_id = get_jwt_identity()
        existing = ShopLikeModel.query.filter_by(user_id=user_id).first()
        if existing:
            if args['downvoted']:
                shoplike.upvoted = False
                shoplike.downvoted = True
            elif args['upvoted']:
                shoplike.upvoted = True
                shoplike.downvoted = False
            else:
                shoplike.upvoted = False
                shoplike.downvoted = False
            db.session.commit()
            return shoplike_schema.dump(shoplike), 200
        return abort(404, message="User haven't upvoted or downvoted")