from pydantic import BaseModel

class BaseSchema(BaseModel):
    class Config:
        @staticmethod
        def alias_generator(string: str) -> str:
            """Konvert snake_case → camelCase"""
            return "".join(
                word.capitalize() if i else word
                for i, word in enumerate(string.split("_"))
            )

        populate_by_name = True
        from_attributes = True
