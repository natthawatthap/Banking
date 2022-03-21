def userEntity(item) -> dict:
    return {
        "account1": item["account1"],
        "amt1": item["amt1"],
        "account2": item["account2"],
        "amt2": item["amt2"],
    }


def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]

def serializeDict(a) -> dict:
    return {**{i: str(a[i]) for i in a if i == '_id'}, **{i: a[i] for i in a if i != '_id'}}


def serializeList(entity) -> list:
    return [serializeDict(a) for a in entity]
