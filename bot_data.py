data = {
    "chat_id": {
        "category_name_1": {
            "sub_category_name_1": {
                "category_id_01": "value",
                "category_id_02": "value",
                "category_id_03": "value"
            },
            "category_id_01": "value",
            "category_id_02": "value",
            "category_id_03": "value"
        },
        "category_name_2": {
            "sub_category_name_2": {
                "category_id_01": "value",
                "category_id_02": "value",
                "category_id_03": "value"
            },
            "category_id_01": "value",
            "category_id_02": "value",
            "category_id_03": "value"
        },
        "category_name_3": {
            "sub_category_name_3": {
                "category_id_01": "value",
                "category_id_02": "value",
                "category_id_03": "value"
            },
            "category_id_01": "value",
            "category_id_02": "value",
            "category_id_03": "value"
        }
    }
}

t = "Lorem ipsum dolor sit amet"
large_list = [t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t]
joined_text = "\n".join([f"{i+1}. {line}" for i, line in enumerate(large_list)])