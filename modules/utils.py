
from fastapi import HTTPException
def pagination(page,per_page,item_count):
    try:
        no_of_pg = int(item_count/int(per_page))
        total_pages = no_of_pg if (item_count % int(per_page)) == 0  else no_of_pg+1
        if int(page)==1:
            return {"total_pages": total_pages}
        return {"total_pages": total_pages,"page":int(page)+1}
    except:
        return {}
