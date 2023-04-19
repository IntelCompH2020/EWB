class Queries:
    def __init__(self) -> None:
        self.Q1 = {}
        self.Q2 = {}

    # Define methods to customize the dictionary objects
    def customize_Q1(self, customizations):
        self.Q1.update(customizations)

    def customize_Q2(self, customizations):
        self.Q2.update(customizations)


# # Customize Q1 with a new key-value pair
# my_queries.customize_Q1({"new_key": "new_value"})