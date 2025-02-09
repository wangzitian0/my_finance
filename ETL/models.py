# ETL/models.py
from neomodel import (
    StructuredNode, StringProperty, DateTimeProperty, FloatProperty,
    IntegerProperty, JSONProperty, RelationshipTo
)
from datetime import datetime

class Info(StructuredNode):
    address1 = StringProperty()
    city = StringProperty()
    state = StringProperty()
    zip = StringProperty()
    country = StringProperty()
    phone = StringProperty()
    website = StringProperty()
    industry = StringProperty()
    industryKey = StringProperty()
    industryDisp = StringProperty()
    sector = StringProperty()
    sectorKey = StringProperty()
    sectorDisp = StringProperty()
    longBusinessSummary = StringProperty()
    fullTimeEmployees = IntegerProperty()
    companyOfficers = JSONProperty()  # 保存公司高管数组信息

class FastInfo(StructuredNode):
    currency = StringProperty()
    dayHigh = FloatProperty()
    dayLow = FloatProperty()
    exchange = StringProperty()
    fiftyDayAverage = FloatProperty()
    lastPrice = FloatProperty()
    lastVolume = IntegerProperty()

class PriceData(StructuredNode):
    # 历史股价数据，每条记录对应一个日期
    date = DateTimeProperty()
    open = FloatProperty()
    high = FloatProperty()
    low = FloatProperty()
    close = FloatProperty()
    volume = IntegerProperty()

class Recommendations(StructuredNode):
    period = JSONProperty()       # 如 {"0": "0m", "1": "-1m", ...}
    strongBuy = JSONProperty()
    buy = JSONProperty()
    hold = JSONProperty()
    sell = JSONProperty()
    strongSell = JSONProperty()

class Sustainability(StructuredNode):
    esgScores = JSONProperty()      # 存储ESG各项分数数据

class Stock(StructuredNode):
    ticker = StringProperty(unique_index=True)
    period = StringProperty()
    interval = StringProperty()
    fetched_at = DateTimeProperty()

    # 关系定义
    info = RelationshipTo(Info, 'HAS_INFO')
    fast_info = RelationshipTo(FastInfo, 'HAS_FAST_INFO')
    prices = RelationshipTo(PriceData, 'HAS_PRICE')
    recommendations = RelationshipTo(Recommendations, 'HAS_RECOMMENDATIONS')
    sustainability = RelationshipTo(Sustainability, 'HAS_SUSTAINABILITY')
