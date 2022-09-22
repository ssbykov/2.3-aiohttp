from aiohttp import web
from models import Advertisement, Session, Base, engine, CreateAdvSchema
import os
from dotenv import load_dotenv
from pydantic.error_wrappers import ValidationError
from errors import BadRequest, NotFound

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = web.Application()


async def get_adv(session, adv_id):
    adv = await session.get(Advertisement, adv_id)
    if adv is None:
        raise NotFound(message='Данного объявления не существует!')
    return adv


class AdvertisementView(web.View):

    async def get(self):
        adv_id = int(self.request.match_info['adv_id'])
        async with app.async_session_maker() as session:
            adv = await get_adv(session, adv_id)
            return web.json_response({
                'heading': adv.heading,
                'description': adv.description,
                'creation_date': str(adv.creation_date),
                'owner': adv.owner
            })

    async def post(self):
        adv_data = await self.request.json()
        try:
            adv_data = CreateAdvSchema(**adv_data).dict()
        except ValidationError as err:
            raise BadRequest(message=err.errors())
        async with app.async_session_maker() as session:
            new_adv = Advertisement(**adv_data)
            session.add(new_adv)
            await session.commit()
            return web.json_response({'status': 'ok', 'id': new_adv.id})

    async def patch(self):
        adv_id = int(self.request.match_info['adv_id'])
        adv_data = await self.request.json()
        async with app.async_session_maker() as session:
            adv = await get_adv(session, adv_id)
            for key, value in adv_data.items():
                setattr(adv, key, value)
            await session.commit()
            return web.json_response({'status': 'ok'})

    async def delete(self):
        adv_id = int(self.request.match_info['adv_id'])
        async with app.async_session_maker() as session:
            adv = await get_adv(session, adv_id)
            await session.delete(adv)
            await session.commit()
            return web.json_response({'status': 'ok'})


async def init_orm(app: web.Application):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        app.async_session_maker = Session
        await conn.commit()
        yield


app.cleanup_ctx.append(init_orm)

app.add_routes([web.post("/advs", AdvertisementView),
               web.patch("/advs/{adv_id:\d+}", AdvertisementView),
               web.delete("/advs/{adv_id:\d+}", AdvertisementView),
               web.get("/advs/{adv_id:\d+}", AdvertisementView)])

if __name__ == '__main__':
    web.run_app(app)
