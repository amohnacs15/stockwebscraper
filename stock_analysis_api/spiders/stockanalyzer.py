# -*- coding: utf-8 -*-
import scrapy
import json

class StockanalyzerSpider(scrapy.Spider):
    name = 'stockanalyzer'
    allowed_domains = ['www.stockanalysis.com', 'api.stockanalysis.com']
    start_urls = ['https://api.stockanalysis.com/wp-json/sa/screener?type=ipoDate']

    focused_companies = dict()

    #primary method that is called from scrapy library
    def parse(self, response):
        self.initFocusedCompaniesDict(json.loads(response.body))
        yield scrapy.Request(
            url=f'https://api.stockanalysis.com/wp-json/sa/screener?type=f',
            callback=self.updateCompaniesWithProfile
        )

    #initial request and filter for IPOs after 2020 and create dict for future work
    def initFocusedCompaniesDict(self, responseIpoDate):
        for object in responseIpoDate:
            ticker = object[0]
            ipoDate = object[1]
            if self.hasRecentIpo(ipoDate):
                self.focused_companies[ticker] = FocusedCompany(ticker, ipoDate) 

        

    def hasRecentIpo(self, ipoDate):
        splitDateArr = ipoDate.split('/')
        return int(splitDateArr[2]) >= 2020

    # second request kicked off from calback
    def updateCompaniesWithProfile(self, response): 
        jsonResponse = json.loads(response.body)
        datas = jsonResponse.get('data')

        for companyProfile in datas:
            ticker = companyProfile.get('s')

            if self.focused_companies.get(ticker) != None:
                tempFocusedCompany = self.focused_companies.get(ticker)
                
                tempFocusedCompany.name = companyProfile.get('n')
                tempFocusedCompany.current_stock_price = companyProfile.get('p')
                tempFocusedCompany.market_cap = companyProfile.get('m')
                tempFocusedCompany.sector = companyProfile.get('se')
                tempFocusedCompany.pe_ratio = companyProfile.get('pe')  

                self.focused_companies[ticker] = tempFocusedCompany  
        yield scrapy.Request(
            url=f'https://api.stockanalysis.com/wp-json/sa/screener?type=profitMargin',
            callback = self.updateCompaniesWithProfitMargin
        )        
    
    def updateCompaniesWithProfitMargin(self, response):
        jsonResponse = json.loads(response.body)
        for object in jsonResponse:
            ticker = object[0]
            
            if (self.focused_companies.get(ticker) != None):
                tempFocusedCompanyProfile = self.focused_companies.get(ticker)
                tempFocusedCompanyProfile.gross_profit_margin = object[1]

                self.focused_companies[ticker] = tempFocusedCompanyProfile  
        yield scrapy.Request(
            url=f'https://api.stockanalysis.com/wp-json/sa/screener?type=grossProfit',
            callback = self.updateCompaniesWithProfit
        )
        

    def updateCompaniesWithProfit(self, response):
        jsonResponse = json.loads(response.body)
        for object in jsonResponse:
            ticker = object[0]
            
            if (self.focused_companies.get(ticker) != None):
                tempFocusedCompanyProfile = self.focused_companies.get(ticker)
                tempFocusedCompanyProfile.gross_profit = object[1]
                self.focused_companies[ticker] = tempFocusedCompanyProfile  
        yield scrapy.Request(
            url=f'https://api.stockanalysis.com/wp-json/sa/screener?type=sharesOut',
            callback = self.updateCompaniesWithSharesOutstanding
        )             

    def updateCompaniesWithSharesOutstanding(self, response):  
        jsonResponse = json.loads(response.body)
        for object in jsonResponse:
            ticker = object[0]
            
            if (self.focused_companies.get(ticker) != None):
                tempFocusedCompanyProfile = self.focused_companies.get(ticker)
                tempFocusedCompanyProfile.total_shares_outstanding = object[1]
                self.focused_companies[ticker] = tempFocusedCompanyProfile    
        yield scrapy.Request(
            url=f'https://api.stockanalysis.com/wp-json/sa/screener?type=ps',
            callback = self.updateCompaniesWithPsRatio
        )   

    def updateCompaniesWithPsRatio(self, response):    
        jsonResponse = json.loads(response.body)
        for object in jsonResponse:
            ticker = object[0]
            
            if (self.focused_companies.get(ticker) != None):
                tempFocusedCompanyProfile = self.focused_companies.get(ticker)
                tempFocusedCompanyProfile.ps_ratio = object[1]
                self.focused_companies[ticker] = tempFocusedCompanyProfile    
        yield scrapy.Request(
            url=f'https://api.stockanalysis.com/wp-json/sa/screener?type=revenue',
            callback = self.updateCompaniesWithRevenue
        ) 

    def updateCompaniesWithRevenue(self, response):   
        jsonResponse = json.loads(response.body)
        for object in jsonResponse:
            ticker = object[0]
            
            if (self.focused_companies.get(ticker) != None):
                tempFocusedCompanyProfile = self.focused_companies.get(ticker)
                tempFocusedCompanyProfile.total_revenue = object[1]
                self.focused_companies[ticker] = tempFocusedCompanyProfile 
        yield scrapy.Request(
            url=f'https://api.stockanalysis.com/wp-json/sa/screener?type=revenueGrowth',
            callback = self.updateCompaniesWithRevenueGrowth
        )   

    def updateCompaniesWithRevenueGrowth(self, response):
        jsonResponse = json.loads(response.body)
        for object in jsonResponse:
            ticker = object[0]
            
            if (self.focused_companies.get(ticker) != None):
                tempFocusedCompanyProfile = self.focused_companies.get(ticker)
                tempFocusedCompanyProfile.revenue_growth_rate_last_year = object[1]
                self.focused_companies[ticker] = tempFocusedCompanyProfile                                          
        
        for x, y in self.focused_companies.items():
            yield {
                "ticker": y.ticker,
                "name": y.name,
                "ipo_date": y.ipo_date,
                "current_stock_price": y.current_stock_price,
                "market_cap": y.market_cap,
                "sector": y.sector,
                "pe_ratio": y.pe_ratio,    
                "gross_profit_margin": y.gross_profit_margin,   
                "gross_profit": y.gross_profit,     
                "total_shares_outstanding": y.total_shares_outstanding,
                "ps_ratio": y.ps_ratio,  
                "total_revenue": y.total_revenue,
                "revenue_growth_rate_last_year": y.revenue_growth_rate_last_year
            }

#teset code, remove
        # for x,y in self.focused_companies.items():
        #     print(x, ":" , str(y.name))
        #     print(x, ":" , y.ipo_date)
        #     print(x, ":" , str(y.current_stock_price))
        #     print(x, ":" , str(y.market_cap))
        #     print(x, ":" , str(y.sector))
        #     print(x, ":" , str(y.pe_ratio))    
        #     print(x, ":", str(y.gross_profit_margin))   
        #     print(x, ":", str(y.gross_profit))     
        #     print(x, ":", str(y.total_shares_outstanding))
        #     print(x, ":", str(y.ps_ratio))  
        #     print(x, ":", str(y.total_revenue))
        #     print(x, ":", str(y.revenue_growth_rate_last_year))

class FocusedCompany():
    ticker = '' #got it!
    name = '' #got it!
    sector = '' #got it!
    ipo_date = '' #got it!

    market_cap = 0 #got it!
    current_stock_price = 0.0 #got it!

    total_revenue = 0 #got it!
    revenue_last_year = 0 
    revenue_current_quarter = 0
    revenue_growth_rate_last_year = 0.0 #got it
    revenue_growth_rate_current_quarter = 0

    gross_profit_margin = 0.0  #got it!
    gross_profit = 0  #got it!
    margin_rate_last_year = 0 
    net_income_loss_last_year = 0 

    earnings_per_share = 0
    total_shares_outstanding = 0 #got it!
    
    ps_ratio = 0.0  #got it!
    pe_ratio = 0.0 #got it!

    def __init__(self, companyTicker, ipoDate):
        self.ticker = companyTicker
        self.ipo_date = ipoDate




                