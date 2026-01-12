# author: Daniel Rode


# https://docs.docker.com/reference/dockerfile/


FROM ghcr.io/mamba-org/micromamba

LABEL Author="Daniel Rode"

# Install SilviMetric
RUN micromamba install --yes silvimetric

# Set SilviMetric
CMD ["silvimetric"]
