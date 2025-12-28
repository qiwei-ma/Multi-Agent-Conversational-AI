import time
import os
from basereal import BaseReal
from logger import logger
from cozepy import Coze, TokenAuth, Message, ChatEventType

client = Coze(
    auth=TokenAuth(token="pat_Xy0g2lsfmDGqztPLrepZtp59zcxS5Kx0uVn6eI1Z8nSD9mq6sBNBu7PP0n4PVaka"), 
    base_url="https://api.coze.cn"
)

# 用字典存储用户ID和会话的映射关系
user_conversations = {}

def llm_init(user_id):
    """初始化或重新创建会话"""
    conversation = client.conversations.create()
    user_conversations[user_id] = conversation
    logger.info(f"Created new conversation with id: {conversation.id}")
    return conversation.id

def get_user_conversation(user_id):
    """获取用户当前会话，如果不存在则创建新会话"""
    if user_id not in user_conversations:
        llm_init(user_id)
    return user_conversations[user_id]

def llm_preprocess(message):
    start = time.perf_counter()
    end = time.perf_counter()
    logger.info(f"llm Time init: {end-start}s")

    Safe = client.chat.stream(
        bot_id="7493358686119755814",
        user_id="@user2170273829",
        additional_messages=[
            Message.build_user_question_text(message)
        ]
    )

    respond = ""
    result = ""
    first = True
    for chunk in Safe:
        if chunk.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            if first:
                end = time.perf_counter()
                logger.info(f"Safe Agent Time to first chunk: {end-start}s")
                first = False
            msg = chunk.message.content
            lastpos = 0
            for i, char in enumerate(msg):
                if char in ",.!;:，。！？：；":
                    result += msg[lastpos:i+1]
                    lastpos = i + 1
                    if len(result) > 10:
                        logger.info(result)
                        respond += result
                        result = ""
            result += msg[lastpos:]
            if len(result) > 0:
                respond += result
                result = ""  # 清空 result

    end = time.perf_counter()
    logger.info(f"Safe Agent Time to last chunk: {end-start}s")
    
    return respond


def llm_response(message,nerfreal:BaseReal, user_id):
    start = time.perf_counter()
    end = time.perf_counter()
    logger.info(f"llm Time init: {end-start}s")
    # 获取用户的会话
    conversation = get_user_conversation(user_id)
    logger.info(f"User {user_id} using conversation.id: {conversation.id}")

    # Safe = client.chat.stream(
    #     bot_id="7493358686119755814",
    #     user_id="@user2170273829",
    #     additional_messages=[
    #         Message.build_user_question_text(message)
    #     ],
    # )

    # respond=""
    # result=""
    # first = True
    # for chunk in Safe:
    #     if chunk.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
    #     # if len(chunk.choices)>0:
    #         #print(chunk.choices[0].delta.content)
    #         if first:
    #             end = time.perf_counter()
    #             logger.info(f"Safe Agent Time to first chunk: {end-start}s")
    #             first = False
    #         msg = chunk.message.content
    #         # msg = chunk.choices[0].delta.content
    #         lastpos=0
    #         #msglist = re.split('[,.!;:，。！?]',msg)
    #         for i, char in enumerate(msg):
    #             if char in ",.!;:，。！？：；" :
    #                 result = result+msg[lastpos:i+1]
    #                 lastpos = i+1
    #                 if len(result)>10:
    #                     logger.info(result)
    #                     # nerfreal.put_msg_txt(result)
    #                     respond = respond + result
    #                     result=""
    #         result = result+msg[lastpos:]
    #         respond = respond + result
    # end = time.perf_counter()
    # logger.info(f"Safe Agent Time to last chunk: {end-start}s")
    # # nerfreal.put_msg_txt(result)    
    # # return respond 
    Feedback = client.chat.stream(
        bot_id="7485272727306764328",
        user_id="@user2170273829",
        additional_messages=[
            Message.build_user_question_text(message)
        ],
        conversation_id=conversation.id,
    )

    respond=""
    result=""
    first = True
    for chunk in Feedback:
        if chunk.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        # if len(chunk.choices)>0:
            #print(chunk.choices[0].delta.content)
            if first:
                end = time.perf_counter()
                logger.info(f"Feedback Agent Time to first chunk: {end-start}s")
                first = False
            msg = chunk.message.content
            # msg = chunk.choices[0].delta.content
            lastpos=0
            #msglist = re.split('[,.!;:，。！?]',msg)
            for i, char in enumerate(msg):
                if char in ",.!;:，。！？：；" :
                    result = result+msg[lastpos:i+1]
                    lastpos = i+1
                    if len(result)>10:
                        logger.info(result)
                        nerfreal.put_msg_txt(result)
                        respond = respond + result
                        result=""
            result = result+msg[lastpos:]
            respond = respond + result
    end = time.perf_counter()
    logger.info(f"Feedback Agent Time to last chunk: {end-start}s")
    nerfreal.put_msg_txt(result)    
    return {
        "response": respond,
        "conversation_id": conversation.id
    }


if __name__ == '__main__':
    print(llm_preprocess("what is your name?"))
