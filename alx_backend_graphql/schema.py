import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    """
    Defines all root query fields available in the API.
    """
    
    hello = graphene.String(
        default_value="Hello, GraphQL!"
    )
    

class Mutation(CRMMutation, graphene.ObjectType): 
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)