__author__ = "Jurriaan van 't Klooster"

import lib.python.querydb as querydb

db = querydb.connect_db()

product = 'vgt_ndvi'
version = 'undefined'
args = {"productcode": product, "version": version}
result = querydb.get_ingestion_product(echo=True, **args)
print "all records:"
result2 = querydb.get_ingestion_product(allrecs=True, echo=True)



from sqlalchemy import func
session = db.session
where = db.ingestion.activated
ingestion_product = session.query(db.ingestion.productcode,
                                  db.ingestion.version,
                                  func.count(db.ingestion.subproductcode), ). \
    group_by(db.ingestion.productcode, db.ingestion.version).filter(where)
print ingestion_product.all()


product = 'vgt_ndvi'
subproduct = 'ndv'
pkey = {"productcode": product, "subproductcode": subproduct}
product_info = querydb.get_product_out_info(echo=True, **pkey)
product_out_params = {"out_data_type": product_info.data_type_id,
                      "out_scale_factor": product_info.scale_factor,
                      "out_scale_offset": product_info.scale_offset,
                      "out_nodata": product_info.nodata}

print product_out_params


args = {"productcode": product,
        "subproductcode": subproduct,
        "datasource_descr_id": 'EO:EUM:DAT:SPOT:S10NDVI'}
product_in_info = querydb.get_product_in_info(echo=True, **args)
product_in_params = {"in_data_type": product_in_info.data_type_id,
                     "in_scale_factor": product_in_info.scale_factor,
                     "in_scale_offset": product_in_info.scale_offset,
                     "in_nodata": product_in_info.no_data,
                     "in_mask_min": product_in_info.scale_offset,
                     "in_mask_max": product_in_info.scale_offset}

print product_in_params


pkey = {"productcode": "vgt_ndvi", "subproductcode": "ndv"}
products = querydb.get_product_info(allrecs=True, echo=True)
product = querydb.get_product_info(echo=True, **pkey)

products = querydb.get_product_native(allrecs=True, echo=True)
product = querydb.get_product_native('ndvi', echo=True)

eumetcasts = querydb.get_eumetcast(allrecs=True, echo=True)
eumetcast = querydb.get_eumetcast('EO:EUM:DAT:SPOT:S10NDVI', echo=True)

internet_ds = querydb.get_internet(allrecs=True, echo=True)
internetds = querydb.get_internet('MOD09GA_Africa', echo=True)

mapsets = querydb.get_mapset(allrecs=True, echo=True)
mapset = querydb.get_mapset('WGS84_Africa_km', echo=True)

pkey = {"productcode": "ndvi", "subproductcode": "ndv"}
ingestions = querydb.get_ingestion(allrecs=True, echo=True)
ingestion = querydb.get_ingestion(echo=True, **pkey)

pkey = {"productcode": "ndvi", "subproductcode": "ndv"}
datasource_descr = querydb.get_datasource_descr(echo=True, source_type='EUMETCAST', source_id='EO:EUM:DAT:SPOTS10NDVI')


row = db.datetype.filter_by(date_type='HHMM').one()
print row


products = db.product.first()
products = db.entity("product").first()
print products

products = db.product.order_by(db.product.productcode).all()
for row in products:
    print row


from sqlalchemy import or_, and_, desc
where = and_(db.product.productcode=='ndvi', db.product.subproductcode=='ndv')
products = db.product.filter(where).order_by(desc(db.product.productcode)).all()
for row in products:
    print row

product = db.product.get('ndvi') # must be single primary key field
print product
product = db.product.filter_by(productcode='ndvi').one()
print product


datetypes = querydb.read_datetypes()
for row in datetypes:
    print row

querydb.create_datetype('JURRIAAN','Dit is een test 123')
datetypes = querydb.read_datetypes()
for row in datetypes:
    print row

querydb.update_datetype('TESTJUR','You can similarly update multiple rows at once.')
datetypes = querydb.read_datetypes()
for row in datetypes:
    print row

querydb.delete_datetype('JURRIAAN')
datetypes = querydb.read_datetypes()
for row in datetypes:
    print row


