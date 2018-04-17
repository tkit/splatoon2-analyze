#!/bin/bash

# stage_list
curl -XPUT 'localhost:9200/_template/splatoon_stages_template?pretty' -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["splatoon_stages*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "stage_history": {
      "properties": {
        "mode": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "rule": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
          },
        "stages": {
          "properties": {
            "name": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            }
          }
        },
        "start_time": {"type": "date"}
      }
    }
  }
}
'

# league_ranking
curl -XPUT 'localhost:9200/_template/splatoon_league?pretty' -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["splatoon_league_ranking*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "league_ranking_history": {
      "properties": {
        "league_ranking_region": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "league_type": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "rule": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
          },
        "stages": {
          "properties": {
            "name": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            }
          }
        },
        "start_time": {"type": "date"},
        "rank": {
          "type": "integer"
        },
        "point": {
          "type": "float"
        },
        "tag_members": {
          "properties": {
            "main_weapon": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "sub_weapon": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "special_weapon": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            }
          }
        }
      }
    }
  }
}
'

# festival_ranking
curl -XPUT 'localhost:9200/_template/splatoon_festival?pretty' -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["splatoon_festival_ranking*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "festival_ranking_history": {
      "properties": {
        "fes_no": {
          "type": "integer"
        },
        "team": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "end_time": {"type": "date"},
        "name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "score": {
          "type": "integer"
        },
        "order": {
          "type": "integer"
        },
        "weapon": {
          "properties": {
            "main_weapon": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "sub_weapon": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "special_weapon": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            }
          }
        },
        "gear": {
          "properties": {
            "part": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "frequent_skill": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "brand": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            }
          }
        }
      }
    }
  }
}
'
