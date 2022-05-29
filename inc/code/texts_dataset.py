class TextsDataset(Dataset):
    """Texts one by one"""

    def __init__(self, tokenizer: PreTrainedTokenizer, path: str, block_size=2048):
        assert os.path.isdir(path)

        block_size = block_size - (tokenizer.max_len - tokenizer.max_len_single_sentence)

        logger.info("Creating features from dataset file at %s", path)

        self.examples = []
        try:
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                with open(file_path, encoding="utf-8") as f:
                    text = f.read()

                tokenized_text = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(text))
                
                logger.info(f"Tokenized {file_path}: tokens len: {len(tokenized_text)}")

                for i in range(0, len(tokenized_text) - block_size + 1, block_size):  # Truncate in block of block_size
                    self.examples.append(
                        tokenizer.build_inputs_with_special_tokens(
                            tokenized_text[i: i + block_size]
                        )
                    )
        except Exception as e:
            logger.exception(e)
        
        logger.info(f"Created dataset of size {len(self.examples)}")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, item):
        return torch.tensor(self.examples[item], dtype=torch.long)