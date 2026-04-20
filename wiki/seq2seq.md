# Seq2seq Models

**Summary**: Seq2seq (sequence-to-sequence) models transform variable-length input sequences into variable-length output sequences, commonly used for machine translation and time series forecasting.

**Sources**: [[Autoregressziós seq2seq – 1. rész]]

**Last updated**: 2026-04-20

---

## The Problem

Traditional approaches fail with variable-length sequences for three reasons:

1. **Variable input length**: Any unit larger than a single word has variable length. Sentences vary in word count, paragraphs vary in sentence count. Feed-forward networks require fixed input size.

2. **Variable output length**: The output length is not known in advance and may differ from input length. Example: Hungarian "Hirdetését olvastam és közlöm önnel, hogy elveszett életkedvének becsületes megtalálója vagyok." (11 words) translates to "I have read your advertisement and I would like to inform you that I am the honest finder of your lost zest for life." (24 words).

3. **Word order matters**: The sequence of words carries information.

## Architecture: Encoder-Decoder

Seq2seq solves this using two specialized neural networks:

### Encoder

The Encoder processes the input sequence and compresses information into a Context Vector (summary vector). This vector theoretically contains all essential information from the input sequence.

### Decoder

The Decoder receives the context vector and generates the output sequence. Unlike feed-forward networks, decoders generate one element at a time.

## Autoregression

Seq2seq uses autoregression: the model's own previous outputs become inputs for the next step.

Example for English translation:

| Step | Input | Expected Output |
|------|-------|--------------|
| 1 | [source words] | "I" |
| 2 | [source words] + ["I"] | "have" |
| 3 | [source words] + ["I", "have"] | "read" |

This is why it's called "autoregressziós" (autoregressive) - the model uses its own generated outputs as context.

## Additional Components

### For Natural Language Processing

- **Embedding**: Text produces sparse matrices. Apply dimensionality reduction to inputs, reverse on decoder outputs.

- **Softmax**: Decoder outputs probabilities. Apply softmax to get the most likely output token.

### For Time Series

These additions are not needed when working with numerical time series data.

## Related pages

- [[neural-networks-basics]]
- [[recurrent-neural-networks]]
- [[time-series-forecasting]]