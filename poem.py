from transformers import pipeline
import keras_gpt_2
import os
import syllapy
from Phyme import Phyme
import random
import json

with open("config.json", "r") as read_file:
        config = json.load(read_file)

config_model = config['generator']['model']
config_top_k = config['generator']['top_k']
config_forbidden = config['generator']['forbidden']

config_structures = config['structures']
config_share_on_twitter = False


if 'twitter' in config:
    import tweepy
    auth = tweepy.OAuthHandler(config['twitter']['consumer_key'], config['twitter']['consumer_secret'])
    auth.set_access_token(config['twitter']['access_token_key'], config['twitter']['access_token_secret'])
    tw = tweepy.API(auth)
    config_share_on_twitter = True




nlp = pipeline("fill-mask", model="distilbert-base-uncased", topk=10)
rhymer = Phyme()

def load_model_and_bpe():
    model_folder = 'models/' + config_model
    config_path = os.path.join(model_folder, 'hparams.json')
    checkpoint_path = os.path.join(model_folder, 'model.ckpt')
    encoder_path = os.path.join(model_folder, 'encoder.json')
    vocab_path = os.path.join(model_folder, 'vocab.bpe')

    text_model = keras_gpt_2.load_trained_model_from_checkpoint(
        config_path, checkpoint_path)
    bpe = keras_gpt_2.get_bpe_from_files(encoder_path, vocab_path)
    
    return text_model, bpe


def make_verse(incipit, syllables_length, should_rhyme_with = False):
    

    incipit = incipit[:1000]

    incipit_length = len(incipit)
    top_k = config_top_k
    errors = 0
    added_words = 0
    
    # We add one word at time until we reach the minimum/maximum length
    
    for i in range(651):
        full_output = keras_gpt_2.generate(text_model, bpe, [incipit], length=1, top_k=top_k)
        full_output = full_output[0]
        print('output', full_output)
        
        newOutput = full_output[len(incipit):]
        print('NEW output', newOutput)

        
        
        if (all(x.isalpha() or x.isspace() for x in newOutput) and all(x not in newOutput for x in config_forbidden)):
            incipit = full_output
            added_words += 1
            errors = 0
        else:
            errors += 1
            if added_words == 0 and errors > 10:
                incipit = incipit + 'and '
            if errors > 10 :
                incipit = incipit + 'and '
        
        
        current_length = len(incipit) - incipit_length
        print('length', current_length)
        
        syllables_count = syllapy.count(full_output[incipit_length:])
        print('syllables', syllables_count )


        print('>>>>>>>>>>>>>>>>>>>>>>>>>>', syllables_count, ' in : ' + full_output[incipit_length:])
        # If we find a line break and the length is greater than the minimum
        # we stop the text generation
        
        if syllables_count == syllables_length:
            print('Syllables length reached')
            break

        
        # If the string is greater than the allowed maximum, we stop the generation
        if syllables_count > syllables_length:
            print('TOO MANY SYLLABLES')
            spaces = [pos for pos, char in enumerate(full_output) if char == ' ']
            # removes 2 last words
            incipit = full_output[:spaces[-2]] 
            


    result = full_output[incipit_length:]

    # we clean double spaces in the result
    for i in range(3):
        result = result.replace('  ', ' ')
    
    result = result.strip()
    
    
    
    
    if should_rhyme_with:
        rhymes = rhymer.get_perfect_rhymes(should_rhyme_with)
        rhyme = should_rhyme_with
        
        print('all rhymes ', rhymes)
    
        all_rhymes = []
    
        if '2' in rhymes and rhymes[2]:
                all_rhymes = rhymes[2]
        else:
            for r in rhymes:
                if rhymes[r]:
                    all_rhymes = rhymes[r]
                    break
            
        print ('rhymes ', all_rhymes)
        
        random.shuffle(all_rhymes)

        for word in all_rhymes:
            print('>>> ', word)
            if(word is not should_rhyme_with and len(word) > 2 and all(x.isalpha() or x.isspace() for x in word)):
                rhyme = word
                break

        print ('choosen ', rhyme)
        
        
        # shorten input to right number of syllables
        
        while True:

            toTest = result + ' ' + rhyme
            syllables_count = syllapy.count(toTest)
            print('checking ', toTest)
            print('syllables ', syllables_count)
            
            if(syllables_count <= syllables_length):
                break
            else:
                spaces = [pos for pos, char in enumerate(result) if char == ' ']
                # removes 2 last words
                result = result[:spaces[-1]] 
                

        while True:
            spaces = [pos for pos, char in enumerate(result) if char == ' ']
            
            if len(spaces) > 2:
                result = result[:spaces[-1]]
            else:
                return False
            
            solutions = nlp( result + ' ' +  nlp.tokenizer.mask_token + ' ' +  rhyme )
            print('solution', solutions)

            acceptable_solution = False
            
            for solution in solutions:
                solution = solution['sequence']
                solution = solution.replace('[CLS]', '')
                solution = solution.replace('[SEP]', '')
                solution = solution.strip()
                
                syllables_count = syllapy.count(solution)
                print (solution, syllables_count)            
                
                if(syllables_count == syllables_length):
                    acceptable_solution = solution
                    break
            
            if acceptable_solution:
                result = acceptable_solution
                break


    result = result.encode('utf-8',errors='ignore').decode('utf-8')
    return result


text_model, bpe = load_model_and_bpe()


def make_poem(structure):
    
    poem = ''
    rhymes = {}
    generated = structure['input'] + "\n"
    
    verses = structure['verses']
    
    # only used if config.twitter exists
    last_twitter_id = ''
    
    for verse in verses:
        
        if 'separator' in verse:
            generated += '\n'
            poem += '\n'
            
            if config_share_on_twitter:
                if(last_twitter_id == ''):
                    status = (config['twitter']['prepend_tweet_with'] + poem)[:280]
                    posted_tweet = tw.update_status(status)
                else:
                    status = poem[:280]
                    posted_tweet = tw.update_status(status, in_reply_to_status_id = last_twitter_id)

                last_twitter_id = posted_tweet.id
                poem = ''
            
        else:
            if verse['rime_with'] in rhymes:
                rhyme_with = rhymes[verse['rime_with']]
            else:
                rhyme_with = False
            
            
            while True:
                new_verse = make_verse(generated, verse['syllables'], should_rhyme_with = rhyme_with )
                if new_verse != False:
                    break
            
            print ('>>> >>> ', new_verse)

            rhymes[verse['rime_with']] = new_verse.split()[-1]
            
            ending = ''
            
            if 'end_with' in verse:
                ending = verse['end_with']
            
            generated += new_verse + ending + '\n'
            poem += new_verse + ending + '\n'
    
    return poem


thePoem = make_poem(random.choice(config_structures))


print ('>>>>>>>>>>>>>>>>>')
print ('>>>>>>>>>>>>>>>>>')
print ('>>>>>>>>>>>>>>>>>')
print (thePoem)

