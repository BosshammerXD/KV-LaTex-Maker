from GeneralDataTypes.IDiedVal import IDiedVal


class IDiedString(IDiedVal[str]):
    def __repr__(self) -> str:
        return f"Var(val={self.val}, id={self.id})"
    
    def __str__(self) -> str:
        return self.val
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, IDiedString):
            return self.val == other.val
        elif isinstance(other, str):
            return self.val == other
        else:
            return False 