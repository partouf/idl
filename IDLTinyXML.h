#pragma once

#include <tinyxml2.h>

using namespace tinyxml2;

template<typename T>
void AddElementToDoc(XMLDocument &doc, XMLNode &parent, const char *name, T value)
{
   XMLElement* element = doc.NewElement(name);
   element->SetText(value);
   parent.InsertEndChild(element);
}
