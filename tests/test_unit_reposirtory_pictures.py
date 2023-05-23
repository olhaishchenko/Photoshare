import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User, Image, Role
from src.repository.pictures import (
    create,
    get_image,
    get_images,
    get_image_from_id,
    get_image_from_url,
    remove
)


class TestImages(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1,
                         roles=Role.user)

    async def test_get_images(self):
        images = [Image(), Image(), Image()]
        self.session.query().filter().offset().limit().all.return_value = images
        result = await get_images(offset=0, limit=3, user=self.user, db=self.session)
        self.assertEqual(result, images)

    async def test_get_image(self):
        image = Image()
        self.session.query().filter().first.return_value = image
        result = await get_image(image_id=1, user=self.user, db=self.session)
        self.assertEqual(result, image)

    async def test_get_image_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_image(image_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create(self):
        image_url='test_url'
        public_id='test_public_id'
        description='test description'
        tags = 'test'
        result = await create(image_url=image_url, tags=tags, description=description, public_id=public_id, user=self.user, db=self.session)
        self.assertEqual(result.image_url, image_url)
        self.assertEqual(result.public_id, public_id)
        self.assertEqual(result.description, description)


    async def test_remove_image(self):
        image = Image()
        self.session.query().filter().first.return_value = image
        result = await remove(image_id=1, user=self.user, db=self.session)
        self.assertEqual(result, image)

    async def test_remove_image_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove(image_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_image_by_id(self):
        image = Image()
        self.session.query().filter().first.return_value = image
        result = await get_image_from_id(image_id=1, user=self.user, db=self.session)
        self.assertEqual(result, image)

    async def test_get_image_by_url(self):
        image = [Image(image_url='test')]
        self.session.query().filter().first.return_value = image
        result = await get_image_from_url(image_url='test', user=self.user, db=self.session)
        self.assertEqual(result, image)

    async def test_get_image_by_id_not_found(self):
        image = []
        self.session.query().filter().first.return_value = image
        result = await get_image_from_id(image_id=4, user=self.user, db=self.session)
        self.assertEqual(result, image)


if __name__ == '__main__':
    unittest.main()
