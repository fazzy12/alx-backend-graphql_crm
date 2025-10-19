import graphene

class Query(graphene.ObjectType):
    """
    Defines all root query fields available in the API.
    """
    
    hello = graphene.String(
        default_value="Hello, GraphQL!"
    )
    

schema = graphene.Schema(query=Query)