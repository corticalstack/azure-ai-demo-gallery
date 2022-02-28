
FROM python:3.7-slim

ARG az_cog_endpoint
ARG az_cog_key
ARG az_cog_region

ENV AZ_COG_ENDPOINT=$az_cog_endpoint
ENV AZ_COG_KEY=$az_cog_key
ENV AZ_COG_REGION=$az_cog_region


WORKDIR /app
ADD . ./

RUN pip install -r requirements.txt

RUN mkdir ~/.streamlit
RUN cp .streamlit/config.prod.toml ~/.streamlit/config.toml
EXPOSE 3000 80 8501

WORKDIR /app

ENTRYPOINT ["streamlit", "run"]
CMD ["main.py"]