from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel, Field


class TelegramGroup(BaseModel):
    language: str = Field(
        description="language of telegram group, for example: Chinese, English, Japanese etc."
    )
    category: str = Field(
        description="category of telegram group. options: Adult，Job, Social, Technology, Programming,\
Games, Music, Movies, Books, Travel, Photography, Food, Fitness, Learning, Language Exchange, \
Art, Design, Entrepreneurship, Investment, Finance, Psychology, Education, History, Politics, Pets,\
 Fashion, Beauty, Cars, Real Estate, Environment, Public Welfare, Sports, Football, Basketball, Anime,\
 Science, Healthcare, Nature, Outdoor Activities, DIY, Home Decor, Parenting, Career Development,\
 Personal Growth, Emotional Exchange, Dark Web, Network Security, Privacy Protection, Hacker\
, Law, Human Rights, Cryptocurrencies, Blockchain, Other"
    )
    tags: list[str] = Field(
        description="tags of telegram group，Note that the tags should be provided in English, maximum 5 tags."
    )


def analyze_group(name: str, desc: str) -> TelegramGroup:
    template = "You are an intelligent Telegram group analysis expert. \
Please carefully analyze the name and description of a\
 Telegram group and provide its language, category, and tags. Note that \
the tags should be provided in English.\n\
{format_instructions}"

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    parser = PydanticOutputParser(pydantic_object=TelegramGroup)

    human_message_prompt = HumanMessagePromptTemplate.from_template(
        "group name:{name}, group description:{desc}\n"
    )

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    llm = ChatOpenAI(temperature=0.2, request_timeout=30)
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    autofix_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
    output = chain.run(
        {
            "format_instructions": parser.get_format_instructions(),
            "name": name,
            "desc": desc,
        }
    )
    return autofix_parser.parse(output)
