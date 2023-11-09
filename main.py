# -*- coding: utf-8 -*-
"""  Postgresql 14.5  Fastapi Pydantic async/await asyncpg Script by js18user. """

import logging
import time
import uvicorn

from enum import Enum
from functools import wraps
from asyncpg import exceptions
from fastapi import FastAPI, Depends, Query, Response
from fastapi_asyncpg import configure_asyncpg
from pydantic import BaseModel, Field


class Crud(str, Enum):
    insert = 'insert'
    update = 'update'
    delete = 'delete'
    select = 'select'


class Table(str, Enum, ):
    user = "user_test"


class User(BaseModel,
           title="This is a Pydantic model for deleting and selecting records in DB Postgresql and API Get and Delete",
           ):
    id: int = Field(
                    default=None,
                    ge=0,
                    description="The id must be greater than zero",
                    examples=[10],
                    strict=True,
    )
    name: str = Field(
                      default=None,
                      min_length=1,
                      description="The name's length must be greater than zero",
                      examples=["Ivan Ivanov"],
                      strict=True,
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Robert Plant",
                },
                {
                    "id": 1,
                },
            ]
        }
    }


class UserInsert(BaseModel,
                 title="This is a Pydantic model for inserting  records into DB Postgresql and API Post",
                 ):
    name: str = Field(
                      min_length=1,
                      description="The name's length must be greater than zero",
                      examples=["Ivan Ivanov"],
                      strict=True,
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "David Coverdale",
                },
            ]
        }
    }


class UserUpdate(BaseModel,
                 title="This is a Pydantic model for updating records into DB Postgresql and API Put",
                 ):
    id: int = Field(
                    ge=0,
                    description="The id must be greater than zero",
                    examples=[10],
                    strict=True,
    )
    name: str = Field(
                      min_length=1,
                      description="The name's length must be greater than zero",
                      examples=["Ivan Ivanov"],
                      strict=True,
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 2,
                    "name": "Jimmy Page",
                },
            ]
        }
    }


def lead_time(func_async):
    @wraps(func_async)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func_async(*args, **kwargs)
        logging.info(
            f"{skip}Function {func_async.__name__} execution time: {int((time.time() - start_time)*1000)} m.sec{skip}"
        )
        return result
    return wrapper


try:
    def db_connect_cloud():
        cone = configure_asyncpg(app, 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
            user='postgres_cloud',
            name='js18user',
            password='aa4401',
            port=5433,
            host="localhost"))
        return cone


    def db_connect():
        cone = configure_asyncpg(app, 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
            user='postgres',
            name='fintech',
            password='aa4401',
            port=5432,
            host="localhost"))
        return cone


    async def query_update(table, model, ):
        """ To create sql query for updating record into database"""
        return ("UPDATE {table} "
                "SET name = '{name}' "
                "WHERE id = {id}  "
                "RETURNING * ;".format(table=table,
                                       id=model['id'],
                                       name=model['name'],
                                       )
                )


    async def query_delete(table, model, ):
        """ To create sql query for deleting the record into database"""
        match model['id']:
            case None:
                match model['name']:
                    case None:
                        pass
                    case _:
                        return f"DELETE FROM {table} WHERE name = '{model['name']}' RETURNING * ;"
            case _:
                return f"DELETE FROM {table}  WHERE id = {model['id']} RETURNING * ;"


    async def query_select(table, model, fields="*"):
        """ To create sql query for selecting  records into database"""
        match model.get('id'):
            case None:
                match model.get('name'):
                    case None:
                        return f"SELECT {fields} FROM {table} ORDER BY name ;"
                    case _:
                        return f"SELECT {fields} FROM {table} WHERE name LIKE '%{model.get('name')}%' ORDER BY name ;"
            case _:
                return f"SELECT {fields} FROM {table}  WHERE id = {model.get('id')} ORDER BY name  ;"


    def query_insert(table, model, ):
        """ To create sql query for creating the new record into database"""
        return "INSERT INTO {table} ( name ) VALUES ('{values}') ON CONFLICT DO NOTHING RETURNING *;".format(
            table=table,
            values=model['name'],
        )


    async def post_processing(db, table, model, response, ):
        row = await insert(db, table=table, model=model, )
        match len(row):
            case 1:
                response.status_code = 200
                return row
            case _:
                return {'message': "A record with the specified attributes already exists into database"}


    @lead_time
    async def insert(db, table, model, ):
        """ To create a new record into DB"""
        async with db.transaction():
            return await db.fetch(query_insert(table, model), )


    @lead_time
    async def select(db, table, model, ):
        """ To select records into DB"""
        return await db.fetch(await query_select(table, model, ), )


    @lead_time
    async def delete(db, table, model, ):
        """ To delete the record into DB"""
        async with db.transaction():
            print(await query_delete(table, model, ))
            return await db.fetch(await query_delete(table, model, ), )


    @lead_time
    async def update(db, table, model, ):
        """ To update the record into DB"""
        async with db.transaction():
            return await db.fetch(await query_update(table, model, ))


    """ ........................................  Starting  .................................."""

    logging.basicConfig(level=logging.INFO,
                        format="%(message)s",
                        )
    create_table = ("CREATE TABLE IF NOT EXISTS users_easy ( "
                    "id SERIAL PRIMARY KEY,  "
                    "name VARCHAR,  "
                    "UNIQUE ( name ) "
                    ");"
                    )
    skip = '\n'
    app = FastAPI(
        title="API documentation",
        description="A set of Api for completing the task is presented",
    )
    conn = db_connect()
    # conn = db_connect_cloud()


    @conn.on_init
    async def initialize_db(db):
        return await db.execute(create_table)


    @app.get('/user/post', status_code=400, description="To create a new record into database", )
    async def user_post_via_get(response: Response,
                                db=Depends(conn.connection),
                                name: str = Query(default=None, min_length=1),
                                ):
        match name:
            case None:
                return {"message": "name argument is not valid"}
            case _:
                return await post_processing(
                    db,
                    table=Table.user,
                    model=UserInsert(name=name).dict(),
                    response=response,
                )


    @app.get('/user', status_code=200, description="To select records from database", )
    async def user_select(response: Response,
                          db=Depends(conn.connection),
                          id: int | str | None = Query(default=None, ge=0, ),
                          name: str | None = Query(default=None, min_length=1),
                          ):
        match id:
            case None:
                pass
            case _:
                match isinstance(id, int):
                    case False:
                        response.status_code = 400
                        return {"message": "Id argument is not valid"}
                    case True:
                        pass
        user = User(id=id,
                    name=name,
                    )
        match user:
            case (user.id | user.name, None):
                model = User().dict()
            case _: model = user.dict()
        row = await select(db,
                           table=Table.user,
                           model=model,
                           )
        match len(row):
            case 0:
                response.status_code = 400
                return {"message": "There are no records with this attributes into database"}
            case _:
                pass
        return row


    @app.post('/user', status_code=400, description="To create a new record into database", )
    async def user_insert(response: Response,
                          user: UserInsert,
                          db=Depends(conn.connection, ),
                          ):
        row = await insert(db, table=Table.user, model=user.dict(), )
        match len(row):
            case 1:
                response.status_code = 200
                return row
            case _:
                return {'message': "A record with the specified attributes already exists into database"}


    @app.delete('/user', status_code=200, description="To delete the record into database", )
    async def user_delete(response: Response,
                          user: User,
                          db=Depends(conn.connection),
                          ):
        model = user.dict()
        if model['id'] is None and model['name'] is None:
            response.status_code = 400
            return {"message": "There are no attributes for the database query"}
        else:
            row = await delete(db, table=Table.user, model=model, )
        match len(row):
            case 0:
                response.status_code = 400
                return {"message": "There are no records in the database with the specified attributes"}
            case _:
                return row


    @app.put('/user', status_code=200, description="To update the record into database", )
    async def user_update(response: Response,
                          user: UserUpdate,
                          db=Depends(conn.connection),
                          ):
        row = await update(db,
                           table=Table.user,
                           model=user.dict(),
                           )
        match len(row):
            case 0:
                response.status_code = 400
                return {"message": "There are no records in the database with the specified attributes"}
            case _:
                return row

except (Exception,
        ValueError,
        TypeError,
        exceptions,
        ) as error_message:
    logging.info(f"Com error: {error_message}")
    pass
else:
    pass


if __name__ == "__main__":

    try:
        uvicorn.run('main:app', host='0.0.0.0', port=8000, )  # reload=True, )
    except KeyboardInterrupt:
        exit()
