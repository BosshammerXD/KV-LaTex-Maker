from .IDiedVal import IDiedVal


class IDiedString(IDiedVal[str]):
    def __str__(self) -> str:
        return self.val
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, IDiedString):
            return self.val == other.val
        elif isinstance(other, str):
            return self.val == other
        else:
            return False 