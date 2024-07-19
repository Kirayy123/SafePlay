#
#
#
#
# # import openai
# #
# # openai.api_key = "sk-7ZCQ3nMwFmzlzIfUF67f11D7457d4b54B64b294d8b42D51a"
# #
# # openai.base_url = "https://free.gpt.ge/v1/"
# # openai.default_headers = {"x-foo": "true"}
# #
# # completion = openai.chat.completions.create(
# #     model="gpt-3.5-turbo",
# #     messages=[
# #         {
# #             "role": "user",
# #             "content": ""
# #         },
# #     ],
# # )
# # print(completion.choices[0].message.content)
# #
# # from openai import OpenAI
# # client = OpenAI(api_key="sk-proj-ICJ2QoFbbqrIA0ubc2UyT3BlbkFJFTAJwQe8NFvmHS21u5Em")
# #
# # completion = client.chat.completions.create(
# #   model="gpt-3.5-turbo",
# #   messages=[
# #     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
# #     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
# #   ]
# # )
# #
# # print(completion.choices[0].message)
#
# from openai import OpenAI
# client = OpenAI(
#     # defaults to os.environ.get("OPENAI_API_KEY")
#     api_key="sk-x9XIbhuccUypiLMq3mqfCiyBqnV0bExnkwUkz3eRxABfLhzd",
#     # base_url="https://api.chatanywhere.tech/v1"
#     base_url="https://api.chatanywhere.cn/v1"
# )
#
# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#     messages=[
#         {
#             "role": "user",
#             "content": "Hello, can you help me?"
#         },
#     ],
# )
#
# print(completion.choices[0].message.content)


# 打开并读取bad_words.txt文件
with open("D:\\Python学习\\bad-words.txt", "r") as file:
    bad_words = [line.strip() for line in file if line.strip()]

BAD_WORD_CHOICES = [(word, word) for word in bad_words]

print(BAD_WORD_CHOICES)

