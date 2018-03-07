import requests

import spacy
nlp = spacy.load('en')
def stemmer(word):
    return nlp(word)[0].lemma_
def pos(word):
    return nlp(word)[0].pos_

from ..concept import Concept
from ..relation import Relation, RELATIONS

WORDNICK_RELATIONHIP_CONVERSION = {
  "synonym": RELATIONS["SYNONYM"],
  "antonym": RELATIONS["ANTONYM"],
  "variant": RELATIONS["IDENTICAL"],
  "equivalent": RELATIONS["IDENTICAL"],
  # "related-word"
  # "form"
  "hypernym": RELATIONS["SUBSET"],
  "hyponym": RELATIONS["SUPERSET"],
  # "inflected-form"
  # "primary"
  "same-context": RELATIONS["SAME_CONTEXT"],
  # "verb-form"
  # "verb-stem"
}

WORDNICK_RELATIONSHIPS = "http://api.wordnik.com/v4/word.json/{}/relatedWords?useCanonical=true&limitPerRelationshipType=10&api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5"

def get_related_concepts(concept):
    url = WORDNICK_RELATIONSHIPS.format(concept)
    response = requests.get(url)

    if response.ok:
        return response.json()
    else:
        raise Exception("Cannot get relations for concept '{}'".format(concept))



MAX_DEPTH = 10

"""
Vocabulary training. This is a good first training round to perform on a concept if nothing is known
about the concept at first. Given a phrase, perform these operations:
1. Create the concept in the concept graph.
2. Use wordnick to determine other concepts that relate to this concept.
3. Create relations between those other concepts. If the other concepts don't exist, vocabulary
train on those concepts first.
4. Lastly, return the new concept.

As an optional parameter, this function takes a max depth to train at. If the training system goes
deeper than the passed depth, it will chop off any traning deepr in the graph than that. The
parameter defaults to 10, but in actual training runs this should be set much higher.
"""
def train(phrase, depth=MAX_DEPTH, stack=[]):
    # Try to prevent training loops. Ie, foo => bar => baz => foo
    if stemmer(phrase) in stack:
        print('  (recursive training loop detected: {} => {})'.format(stack, phrase))
        return None

    if depth == 0:
        print('  (max depth, stopping.)')
        return None

    print("* Training on '{}'".format(phrase))

    base_concept = Concept.find(phrase)
    if base_concept is None:
        base_concept = Concept(phrase, pos(phrase))
        base_concept.save()

        related_concepts = get_related_concepts(phrase)

        for conc in related_concepts:
            # Figure out the type of relationship that was found.
            relation_type = WORDNICK_RELATIONHIP_CONVERSION.get(conc["relationshipType"])
            if relation_type is None:
                # print(
                #     "  Found concept that has relationship '{}', unsure how to handle that. Continuing...".format(
                #         conc["relationshipType"]
                #     )
                # )
                continue

            # Loop through each word in the relationship
            words = conc["words"]
            for word in words:
                related_concept = Concept.find(word)

                # If the related concept doesn't exist, create it first.
                if related_concept is None:
                    # Add a new item to the end of the stack
                    new_stack = stack[:]
                    new_stack.append(base_concept.name)

                    # Train against the new concept
                    train(word, depth-1, new_stack)

                    related_concept = Concept.find(word)
                    if related_concept is None:
                        continue

                # Create the relationship
                print("  Relating '{}' => '{}'".format(base_concept.name, related_concept.name))
                base_concept.add_relation(relation_type, related_concept)

    return base_concept
