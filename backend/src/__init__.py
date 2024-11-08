from flask import Flask
from flask_cors import CORS
from flask_restx import Resource, Api
from flask_pymongo import PyMongo
from pymongo.collection import Collection
from .model import Company
from flask import request
from src.llm.groq_llm import GroqClient

# Configure Flask & Flask-PyMongo:
# python app.py run
app = Flask(__name__)
# allow access from any frontend
cors = CORS()
cors.init_app(app, resources={r"*": {"origins": "*"}})
# add your mongodb URI
app.config["MONGO_URI"] = "mongodb://localhost:27017/companiesdatabase"
pymongo = PyMongo(app)
# Get a reference to the companies collection.
companies: Collection = pymongo.db.companies
api = Api(app)
class CompaniesList(Resource):
    def get(self, args=None):
        # retrieve the arguments and convert to a dict
        args = request.args.to_dict()
        print(args)
        # If the user specified category is "All" we retrieve all companies
        if args['category'] == 'All':
            cursor = companies.find()
        # In any other case, we only return the companies where the category applies
        else:
            cursor = companies.find(args)
        # we return all companies as json
        return [Company(**doc).to_json() for doc in cursor]

class Companies(Resource):
    def get(self, id):
        import pandas as pd
        from statsmodels.tsa.ar_model import AutoReg
        # search for the company by ID
        cursor = companies.find_one_or_404({"id": id})
        company = Company(**cursor)
        # retrieve args
        args = request.args.to_dict()
        # retrieve the profit
        profit = company.profit
        # add to df
        profit_df = pd.DataFrame(profit).iloc[::-1]
        if args['algorithm'] == 'random':
            # retrieve the profit value from 2021
            prediction_value = int(profit_df["value"].iloc[-1])
            # add the value to profit list at position 0
            company.profit.insert(0, {'year': 2022, 'value': prediction_value})
        elif args['algorithm'] == 'regression':
            # create model
            model_ag = AutoReg(endog=profit_df['value'], lags=1, trend='c', seasonal=False, exog=None, hold_back=None,
                               period=None, missing='none')
            # train the model
            fit_ag = model_ag.fit()
            # predict for 2022 based on the profit data
            prediction_value = fit_ag.predict(start=len(profit_df), end=len(profit_df), dynamic=False).values[0]
            # add the value to profit list at position 0
            company.profit.insert(0, {'year': 2022, 'value': prediction_value})
        return company.to_json()


class GroqAPIPoem(Resource):
    def get(self, id):
        # Create GroqClient instance
        client = GroqClient()
        cursor = companies.find_one_or_404({"id": id})
        company = Company(**cursor)

        # Call the generate_info method with company name and prompt
        response = client.generate_poem(company.name, 'src/llm/prompts/groq_api_poem.json')
        print(response)

        # Return the Groq API response as JSON
        return {"result": response}, 200

class GroqAPIFact(Resource):
    def get(self, id):
        # Create GroqClient instance
        client = GroqClient()
        cursor = companies.find_one_or_404({"id": id})
        company = Company(**cursor)

        # Call the generate_info method with company name and prompt
        response = client.generate_poem(company.name, 'src/llm/prompts/groq_api_fact.json')
        print(response)

        # Return the Groq API response as JSON
        return {"result": response}, 200

api.add_resource(CompaniesList, '/companies')
api.add_resource(Companies, '/companies/<int:id>')
api.add_resource(GroqAPIPoem, '/groq/poem/<int:id>')
api.add_resource(GroqAPIFact, '/groq/fact/<int:id>')
