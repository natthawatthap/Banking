from enum import Enum
import json
from unicodedata import name
from bson import ObjectId
from fastapi import APIRouter, status, Response
from bson import ObjectId
from passlib.hash import sha256_crypt
from starlette.status import HTTP_204_NO_CONTENT
from models.transaction import Transaction

from models.user import User
from config.db import db
from schemas.user import userEntity, usersEntity
from bson.json_util import dumps, loads

user = APIRouter()

# Create a new bank account for a customer, with an initial deposit amount. A single customer may have multiple bank accounts.
@user.post('/user', tags=["User"])
async def create_account(user: User):
    new_user = dict(user)
    del new_user["id"]
    if user.amt < 0:
        return {"message": "amt must be more than 0"}

    db.bankDB.account.insert_one(new_user).inserted_id
    return {"message": "Account created successfully."}


# Retrieve balances for a given account.
@user.get('/user/{id}', response_model=User, tags=["User"])
async def retrieve_balances(id: str):

    user = db.bankDB.account.find_one({"_id": ObjectId(id)})
    return dict(user)

# Transfer amounts between any two accounts, including those owned by different customers.
@user.post("/transfer", tags=["Transaction"])
async def transfer_amt(id1: str, amt: float, id2: str,):

    # Check the original amount
    user1 = dict(db.bankDB.account.find_one({"_id": ObjectId(id1)}))
    if user1["amt"] < amt:
        return {"message": "Your balance is not enough."}

    db.bankDB.account.find_one_and_update({
        "_id": ObjectId(id1)
    }, {
        "$set": {"amt": user1["amt"] - amt}
    })

    user2 = dict(db.bankDB.account.find_one({"_id": ObjectId(id2)}))

    db.bankDB.account.find_one_and_update({
        "_id": ObjectId(id2)
    }, {
        "$set": {"amt": user2["amt"] + amt}
    })

    transaction = {
        "account1": id1,
        "amt1": -amt,
        "account2": id2,
        "amt2": +amt,
    }

    db.bankDB.history.insert_one(transaction).inserted_id

    return {"message": "Successful transaction."}


# Retrieve transfer history for a given account.
@user.get('/transaction/{id}', tags=["Transaction"])
async def retrieve_transaction(id: str):
    user = db.bankDB.history.find({"account1":id},{"_id":0})

    return usersEntity(user)

