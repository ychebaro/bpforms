""" Classes to represent modified forms of DNA, RNA, and proteins

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2019-01-31
:Copyright: 2019, Karr Lab
:License: MIT
"""

from wc_utils.util.chem import EmpiricalFormula
import capturer
with capturer.CaptureOutput(merged=False, relay=False):
    from cdk_pywrapper import cdk_pywrapper
import attrdict
import lark
import openbabel
import re


class Identifier(object):
    """ A identifier in a namespace for an external database

    Attributes:
        ns (:obj:`str`): namespace
        id (:obj:`str`): id in namespace
    """

    def __init__(self, ns, id):
        """
        Args:
            ns (:obj:`str`): namespace
            id (:obj:`str`): id in namespace
        """
        self.ns = ns
        self.id = id

    @property
    def ns(self):
        """ Get the namespace 

        Returns:
            :obj:`str`: namespace
        """
        return self._ns

    @ns.setter
    def ns(self, value):
        """ Set the namespace

        Args:
            value (:obj:`str`): namespace

        Raises:
            :obj:`ValueError`: if the namespace is not a series of letters, numbers, dashes, underscores, and periods
        """
        if not isinstance(value, str) or not re.match(r'^[A-Za-z0-9_\.\-]+$', value):
            raise ValueError('`ns` must be a series of letters, numbers, dashes, underscores, and periods')
        self._ns = value

    @property
    def id(self):
        """ Get the id 

        Returns:
            :obj:`str`: id
        """
        return self._id

    @id.setter
    def id(self, value):
        """ Set the id

        Args:
            value (:obj:`str`): id

        Raises:
            :obj:`ValueError`: if the id is not a series of letters, numbers, dashes, underscores, periods, and colons
        """
        if not isinstance(value, str) or not re.match(r'^[A-Za-z0-9_\.\-:]+$', value):
            raise ValueError('`id` must be a series of letters, numbers, dashes, underscores, periods, and colons')
        self._id = value

    def __eq__(self, other):
        """ Check if two identifiers are semantically equal

        Args:
            other (:obj:`Identifier`): another identifier

        Returns:
            :obj:`bool`: True, if the identifiers are semantically equal
        """
        return self is other or (self.__class__ == other.__class__ and self.ns == other.ns and self.id == other.id)

    def __hash__(self):
        """ Generate a hash

        Returns:
            :obj:`int`: hash
        """
        return hash((self.ns, self.id))


class IdentifierSet(set):
    """ Set of identifiers """

    def __init__(self, identifiers=None):
        """
        Args:
            identifiers (:obj:iterable of :obj:`Identifier`): iterable of identifiers
        """
        super(IdentifierSet, self).__init__()
        if identifiers is not None:
            for identifier in identifiers:
                self.add(identifier)

    def add(self, identifier):
        """ Add an identifier 

        Args:
            identifier (:obj:`Identifier`): identifier 

        Raises:
            :obj:`ValueError`: if the `identifier` is not an instance of `Indentifier`
        """
        if not isinstance(identifier, Identifier):
            raise ValueError('`identifier` must be an instance of `Indentifier`')
        super(IdentifierSet, self).add(identifier)

    def update(self, identifiers):
        """ Add a set of identifiers 

        Args:
            identifiers (iterable of :obj:`Identifier`): identifiers
        """
        for identifier in identifiers:
            self.add(identifier)

    def symmetric_difference_update(self, other):
        """ Remove common elements with other and add elements from other not in self 

        Args:
            other (:obj:`IdentifierSet`): other set of identifiers
        """
        if not isinstance(other, IdentifierSet):
            other = IdentifierSet(other)
        super(IdentifierSet, self).symmetric_difference_update(other)


class SynonymSet(set):
    """ Set of synonyms """

    def __init__(self, synonyms=None):
        """
        Args:
            synonyms (:obj:iterable of :obj:`str`): iterable of synonyms

        Raises:
            :obj:`ValueError`: if synonyms is not an iterable of string
        """
        super(SynonymSet, self).__init__()
        if isinstance(synonyms, str):
            raise ValueError('synonyms must be an iterable of strings')
        if synonyms is not None:
            for synonym in synonyms:
                self.add(synonym)

    def add(self, synonym):
        """ Add an synonym 

        Args:
            synonym (:obj:`str`): synonym 

        Raises:
            :obj:`ValueError`: if the `synonym` is not an instance of `Indentifier`
        """
        if not synonym or not isinstance(synonym, str):
            raise ValueError('`synonyms` must be a non-empty string')
        super(SynonymSet, self).add(synonym)

    def update(self, synonyms):
        """ Add a set of synonyms 

        Args:
            synonyms (iterable of :obj:`SynonymSet`): synonyms
        """
        for synonym in synonyms:
            self.add(synonym)

    def symmetric_difference_update(self, other):
        """ Remove common synonyms with other and add synonyms from other not in self 

        Args:
            other (:obj:`SynonymSet`): other set of synonyms
        """
        if not isinstance(other, SynonymSet):
            other = SynonymSet(other)
        super(SynonymSet, self).symmetric_difference_update(other)


class Base(object):
    """ A base in a biopolymer

    Attributes:
        id (:obj:`str`): id
        name (:obj:`str`): name
        synonyms (:obj:`set` of :obj:`str`): synonyms        
        identifiers (:obj:`set` of :obj:`Identifier`, optional): identifiers in namespaces for external databases
        structure (:obj:`openbabel.OBMol`): chemical structure
        delta_mass (:obj:`float`): additional mass (Dalton) relative to structure
        delta_charge (:obj:`int`): additional charge relative to structure
        start_position (:obj:`tuple`): uncertainty in location of base
        end_position (:obj:`tuple`): uncertainty in location of base
        comments (:obj:`str`): comments
    """

    def __init__(self, id=None, name=None, synonyms=None, identifiers=None, structure=None,
                 delta_mass=None, delta_charge=None, start_position=None, end_position=None, comments=None):
        """
        Attributes:
            id (:obj:`str`, optional): id
            name (:obj:`str`, optional): name
            synonyms (:obj:`set` of :obj:`str`, optional): synonyms
            identifiers (:obj:`set` of :obj:`Identifier`, optional): identifiers in namespaces for external databases
            structure (:obj:`openbabel.OBMol` or :obj:`str`, optional): chemical structure
            delta_mass (:obj:`float`, optional): additional mass (Dalton) relative to structure
            delta_charge (:obj:`float`, optional): additional charge relative to structure
            start_position (:obj:`int`, optional): uncertainty in location of base
            end_position (:obj:`int`, optional): uncertainty in location of base
            comments (:obj:`str`, optional): comments
        """
        self.id = id
        self.name = name
        self.synonyms = synonyms or SynonymSet()
        self.identifiers = identifiers or IdentifierSet()
        self.structure = structure
        self.delta_mass = delta_mass
        self.delta_charge = delta_charge
        self.start_position = start_position
        self.end_position = end_position
        self.comments = comments

    @property
    def id(self):
        """ Get id 

        Returns:
            :obj:`str`: id
        """
        return self._id

    @id.setter
    def id(self, value):
        """ Set id 

        Args:
            value (:obj:`str`): id

        Raises:
            :obj:`ValueError`: if `value` is not a a string or None
        """
        if value and not isinstance(value, str):
            raise ValueError('`id` must be a string or None')
        self._id = value

    @property
    def name(self):
        """ Get name 

        Returns:
            :obj:`str`: name
        """
        return self._name

    @name.setter
    def name(self, value):
        """ Set name 

        Args:
            value (:obj:`str`): name

        Raises:
            :obj:`ValueError`: if `value` is not a a string or None
        """
        if value and not isinstance(value, str):
            raise ValueError('`name` must be a string or None')
        self._name = value

    @property
    def synonyms(self):
        """ Get synonyms 

        Returns:
            :obj:`SynonymSet`: synonyms
        """
        return self._synonyms

    @synonyms.setter
    def synonyms(self, value):
        """ Set synonyms

        Args:
            value (:obj:`SynonymSet`): synonyms

        Raises:
            :obj:`ValueError`: if `synonyms` is not an instance of `SynonymSet`
        """
        if value is None:
            raise ValueError('`synonyms` must be an instance `SynonymSet`')
        if not isinstance(value, SynonymSet):
            value = SynonymSet(value)
        self._synonyms = value

    @property
    def identifiers(self):
        """ Get identifiers 

        Returns:
            :obj:`IdentifierSet`: identifiers
        """
        return self._identifiers

    @identifiers.setter
    def identifiers(self, value):
        """ Set identifiers

        Args:
            value (:obj:`IdentifierSet`): identifiers

        Raises:
            :obj:`ValueError`: if `identifiers` is not an instance of `Indentifiers`
        """
        if value is None:
            raise ValueError('`identifiers` must be an instance `Indentifiers`')
        if not isinstance(value, IdentifierSet):
            value = IdentifierSet(value)
        self._identifiers = value

    @property
    def structure(self):
        """ Get structure 

        Returns:
            :obj:`openbabel.OBMol`: structure
        """
        return self._structure

    @structure.setter
    def structure(self, value):
        """ Set structure

        Args:
            value (:obj:`openbabel.OBMol` or :obj:`str`): OpenBabel molecule, InChI-encoded structure, or None

        Raises:
            :obj:`ValueError`: if value is not an OpenBabel molecule, InChI-encoded structure, or None
        """
        if value and not isinstance(value, openbabel.OBMol):
            ob_mol = openbabel.OBMol()
            conversion = openbabel.OBConversion()
            assert conversion.SetInFormat('inchi'), 'Unable to set format to inchi'
            if not conversion.ReadString(ob_mol, value):
                raise ValueError('`structure` must be an OpenBabel molecule, InChI-encoded structure, or None')
            value = ob_mol

        self._structure = value or None

    @property
    def delta_mass(self):
        """ Get extra mass 

        Returns:
            :obj:`float`: extra mass
        """
        return self._delta_mass

    @delta_mass.setter
    def delta_mass(self, value):
        """ Set extra mass

        Args:
            value (:obj:`float`): extra mass

        Raises:
            :obj:`ValueError`: if value is not a float or None
        """
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError('`delta_mass` must be a float or None')
            value = float(value)
        self._delta_mass = value

    @property
    def delta_charge(self):
        """ Get extra charge 

        Returns:
            :obj:`int`: extra charge
        """
        return self._delta_charge

    @delta_charge.setter
    def delta_charge(self, value):
        """ Set extra charge

        Args:
            value (:obj:`int`): extra charge

        Raises:
            :obj:`ValueError`: if value is not an int or None
        """
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError('`delta_charge` must be an integer or None')
            if value != int(value):
                raise ValueError('`delta_charge` must be an integer or None')
            value = int(value)
        self._delta_charge = value

    @property
    def start_position(self):
        """ Get start position 

        Returns:
            :obj:`int`: start position
        """
        return self._start_position

    @start_position.setter
    def start_position(self, value):
        """ Set start position

        Args:
            value (:obj:`float`): start position

        Raises:
            :obj:`ValueError`: if value is not an int or None
        """
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError('`start_position` must be a positive integer or None')
            if value != int(value) or value < 1:
                raise ValueError('`start_position` must be a positive integer or None')
            value = int(value)
        self._start_position = value

    @property
    def end_position(self):
        """ Get end position

        Returns:
            :obj:`int`: end position
        """
        return self._end_position

    @end_position.setter
    def end_position(self, value):
        """ Set end position

        Args:
            value (:obj:`float`): end position

        Raises:
            :obj:`ValueError`: if value is not an int or None
        """
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError('`end_position` must be a positive integer or None')
            if value != int(value) or value < 1:
                raise ValueError('`end_position` must be a positive integer or None')
            value = int(value)
        self._end_position = value

    @property
    def comments(self):
        """ Get comments 

        Returns:
            :obj:`str`: comments
        """
        return self._comments

    @comments.setter
    def comments(self, value):
        """ Set comments

        Args:
            value (:obj:`str`): comments

        Raises:
            :obj:`ValueError`: if value is not a str or None
        """
        if value and not isinstance(value, str):
            raise ValueError('`comments` must be a string or None')
        self._comments = value

    def protonate(self, ph):
        """ Update to the major protonation state at the pH 

        Args:
            ph (:obj:`float`): pH
        """
        if self.structure:
            self.structure.CorrectForPH(ph)

    def get_inchi(self):
        """ Get InChI representration of structure

        Returns:
            :obj:`str`: InChI representration of structure
        """
        if self.structure:
            conversion = openbabel.OBConversion()
            assert conversion.SetOutFormat('smi'), 'Unable to set format to smiles'
            compound = cdk_pywrapper.Compound(compound_string=conversion.WriteString(self.structure).strip(), identifier_type='smiles')
            return compound.get_inchi()
        else:
            return None

    def get_formula(self):
        """ Get the chemical formula

        Returns:
            :obj:`EmpiricalFormula`: chemical formula
        """
        if self.structure:
            el_table = openbabel.OBElementTable()
            formula = {}
            mass = 0
            for i_atom in range(self.structure.NumAtoms()):
                atom = self.structure.GetAtom(i_atom + 1)
                el = el_table.GetSymbol(atom.GetAtomicNum())
                if el in formula:
                    formula[el] += 1
                else:
                    formula[el] = 1
                mass += el_table.GetMass(atom.GetAtomicNum())
            formula = EmpiricalFormula(formula)

            # calc hydrogens because OpenBabel doesn't output this
            formula['H'] = round((self.structure.GetMolWt() - mass) / el_table.GetMass(1))
            return formula
        else:
            return None

    def get_mol_wt(self):
        """ Get the molecular weight

        Returns:
            :obj:`float`: molecular weight
        """
        if self.structure:
            return self.get_formula().get_molecular_weight() + (self.delta_mass or 0.)
        return None

    def get_charge(self):
        """ Get the charge

        Returns:
            :obj:`int`: charge
        """
        if self.structure:
            return self.structure.GetTotalCharge() + (self.delta_charge or 0)
        return None

    def __str__(self):
        """ Get a string representation of the base

        Returns:
            :obj:`str`: string representation of the base
        """
        els = []
        if self.id:
            els.append('id: "' + self.id + '"')
        if self.name:
            els.append('name: "' + self.name.replace('"', '\\"') + '"')
        for synonym in self.synonyms:
            els.append('synonym: "' + synonym.replace('"', '\\"') + '"')
        for identifier in self.identifiers:
            els.append('identifier: ' + identifier.ns + '/' + identifier.id)
        if self.structure:
            els.append('structure: ' + self.get_inchi())
        if self.delta_mass is not None:
            els.append('delta-mass: ' + str(self.delta_mass))
        if self.delta_charge is not None:
            els.append('delta-charge: ' + str(self.delta_charge))
        if self.start_position is not None or self.end_position is not None:
            els.append('position: {}-{}'.format(self.start_position or '', self.end_position or ''))
        if self.comments:
            els.append('comments: "' + self.comments.replace('"', '\\"') + '"')

        return '[' + ' | '.join(els) + ']'

    def is_equal(self, other):
        """ Check if two bases are semantically equal

        Args:
            other (:obj:`Base'): another base

        Returns:
            :obj:`bool`: :obj:`True`, if the objects have the same structure
        """
        if self is other:
            return True
        if self.__class__ != other.__class__:
            return False

        attrs = ['id', 'name', 'synonyms', 'identifiers',
                 'delta_mass', 'delta_charge', 'start_position', 'end_position',
                 'comments']
        for attr in attrs:
            if getattr(self, attr) != getattr(other, attr):
                return False

        if self.get_inchi() != other.get_inchi():
            return False

        return True


class BaseSequence(list):
    """ Sequence of bases """

    def __init__(self, bases=None):
        """
        Args:
            bases (:obj:iterable of :obj:`Base`): iterable of bases
        """
        super(BaseSequence, self).__init__()
        if bases is not None:
            for base in bases:
                self.append(base)

    def append(self, base):
        """ Add a base 

        Args:
            base (:obj:`Base`): base 

        Raises:
            :obj:`ValueError`: if the `base` is not an instance of `Base`
        """
        if not isinstance(base, Base):
            raise ValueError('`base` must be an instance of `Base`')
        super(BaseSequence, self).append(base)

    def extend(self, bases):
        """ Add a list of bases 

        Args:
            bases (iterable of :obj:`Base`): iterable of bases
        """
        for base in bases:
            self.append(base)

    def insert(self, i, base):
        """ Insert a base at a position

        Args:
            i (:obj:`int`): position to insert base
            base (:obj:`Base`): base 
        """
        if not isinstance(base, Base):
            raise ValueError('`base` must be an instance of `Base`')
        super(BaseSequence, self).insert(i, base)

    def __setitem__(self, slice, base):
        """ Set base(s) at slice

        Args:
            slice (:obj:`int` or :obj:`slice`): position(s) to set base
            base (:obj:`Base` or :obj:`list` of :obj:`Base`): base or bases
        """
        if isinstance(slice, int):
            if not isinstance(base, Base):
                raise ValueError('`base` must be a `Base`')
        else:
            for b in base:
                if not isinstance(b, Base):
                    raise ValueError('`base` must be an iterable of `Base`')

        super(BaseSequence, self).__setitem__(slice, base)

    def get_base_counts(self):
        """ Get the frequency of each base within the sequence

        Returns:
            :obj:`dict`: dictionary that maps bases to their counts
        """
        counts = {}
        for base in self:
            if base in counts:
                counts[base] += 1
            else:
                counts[base] = 1
        return counts

    def is_equal(self, other):
        """ Determine if two base sequences are semantically equal 

        Args:
            other (:obj:`BaseSequence`): other base sequence

        Returns:
            :obj:`bool`: True, of the base sequences are semantically equal
        """
        if self is other:
            return True
        if self.__class__ != other.__class__ or len(self) != len(other):
            return False
        for self_base, other_base in zip(self, other):
            if not self_base.is_equal(other_base):
                return False
        return True


class Alphabet(attrdict.AttrDict):
    """ Alphabet for bases """

    def protonate(self, ph):
        """ Protonate bases 

        Args:
            ph (:obj:`float`): pH
        """
        for base in self.values():
            base.protonate(ph)

    def is_equal(self, other):
        """ Determine two alphabets are semantically equal

        Args:
            other (:obj:`type`): other alphabet

        Returns:
            :obj:`bool`: True, if the alphabets are semantically equal
        """
        if self is other:
            return True
        if self.__class__ != other.__class__:
            return False
        if len(self) != len(other):
            return False
        for chars, self_base in self.items():
            if not self_base.is_equal(other.get(chars, None)):
                return False
        return True


class BpForm(object):
    """ Biopolymer form 

    Attributes:
        base_seq (:obj:`BaseSequence`): bases of the biopolymer
        alphabet (:obj:`Alphabet`): base alphabet
        bond_formula (:obj:`EmpiricalFormula`): empirical formula for bonds between bases
        bond_charge (:obj:`int`): charge of bonds between bases

        DEFAULT_ALPHABET (:obj:`Alphabet`): default base alphabet
        DEFAULT_BOND_FORMULA (:obj:`EmpiricalFormula`): default empirical formula for bonds between bases
        DEFAULT_BOND_CHARGE (:obj:`int`): default charge of bonds between bases

        _parser (:obj:`lark.Lark`): parser
    """
    DEFAULT_ALPHABET = None
    DEFAULT_BOND_FORMULA = None
    DEFAULT_BOND_CHARGE = None

    def __init__(self, base_seq=None, alphabet=None, bond_formula=None, bond_charge=None):
        """
        Args:
            base_seq (:obj:`BaseSequence`, optional): bases of the biopolymer
            alphabet (:obj:`Alphabet`, optional): base alphabet
            bond_formula (:obj:`EmpiricalFormula`, optional): empirical formula for bonds between bases
            bond_charge (:obj:`int`, optional): charge of bonds between bases
        """
        if alphabet is None:
            alphabet = self.DEFAULT_ALPHABET or Alphabet()
        if bond_formula is None:
            bond_formula = self.DEFAULT_BOND_FORMULA or EmpiricalFormula()
        if bond_charge is None:
            bond_charge = self.DEFAULT_BOND_CHARGE or 0

        self.base_seq = base_seq or BaseSequence()
        self.alphabet = alphabet
        self.bond_formula = bond_formula
        self.bond_charge = bond_charge

    @property
    def base_seq(self):
        """ Get the base sequence

        Returns:
            :obj:`BaseSequence`: base sequence
        """
        return self._base_seq

    @base_seq.setter
    def base_seq(self, value):
        """ Set the base sequence

        Args:
            value (:obj:`BaseSequence`): base sequence

        Raises:
            :obj:`ValueError`: if `base_seq` is not an instance of `BaseSequence`
        """
        if value is None:
            raise ValueError('`base_seq` must be an instance of `BaseSequence`')
        if not isinstance(value, BaseSequence):
            value = BaseSequence(value)
        self._base_seq = value

    @property
    def alphabet(self):
        """ Get the alphabet

        Returns:
            :obj:`Alphabet`: alphabet
        """
        return self._alphabet

    @alphabet.setter
    def alphabet(self, value):
        """ Set the base sequence

        Args:
            value (:obj:`Alphabet`): alphabet

        Raises:
            :obj:`ValueError`: if `alphabet` is not an instance of `Alphabet`
        """
        if not isinstance(value, Alphabet):
            raise ValueError('`alphabet` must be an instance of `Alphabet`')
        self._alphabet = value

    @property
    def bond_formula(self):
        """ Get the formula of the bonds 

        Returns:
            :obj:`EmpiricalFormula`: formula of the bonds
        """
        return self._bond_formula

    @bond_formula.setter
    def bond_formula(self, value):
        """ Set the formula of the bonds

        Args:
            value (:obj:`EmpiricalFormula` or :obj:`str`): formula of the bonds
        """
        if not isinstance(value, EmpiricalFormula):
            value = EmpiricalFormula(value)
        self._bond_mol_wt = value.get_molecular_weight()
        self._bond_formula = value

    @property
    def bond_charge(self):
        """ Get the bond charge 

        Returns:
            :obj:`str`: bond charge
        """
        return self._bond_charge

    @bond_charge.setter
    def bond_charge(self, value):
        """ Set the bond charge

        Args:
            value (:obj:`str`): bond charge

        Raises:
            :obj:`ValueError`: if the bond charge is not a series of letters, numbers, dashes, underscores, and periods
        """
        if not isinstance(value, (int, float)) or value != int(value):
            raise ValueError('`bond_charge` must be an integer')
        self._bond_charge = int(value)

    def is_equal(self, other):
        """ Check if two biopolymer forms are semantically equal

        Args:
            other (:obj:`BpForm'): another biopolymer form

        Returns:
            :obj:`bool`: :obj:`True`, if the objects have the same structure
        """
        return self is other or (self.__class__ == other.__class__
                                 and self.base_seq.is_equal(other.base_seq)
                                 and self.alphabet.is_equal(other.alphabet)
                                 and self.bond_formula == other.bond_formula
                                 and self.bond_charge == other.bond_charge)

    def __getitem__(self, slice):
        """ Get base(s) at slice

        Args:   
            slice (:obj:`int` or :obj:`slice`): position(s)

        Returns:
            :obj:`Base` or :obj:`Bases`: base or bases
        """
        return self.base_seq.__getitem__(slice)

    def __setitem__(self, slice, base):
        """ Set base(s) at slice

        Args:   
            slice (:obj:`int` or :obj:`slice`): position(s)
            base (:obj:`Base` or :obj:`Bases`): base or bases
        """
        self.base_seq.__setitem__(slice, base)

    def __delitem__(self, slice):
        """ Delete base(s) at slice

        Args:   
            slice (:obj:`int` or :obj:`slice`): position(s)
        """
        self.base_seq.__delitem__(slice)

    def __iter__(self):
        """ Get iterator over base sequence 

        Returns:
            :obj:`iterator` of :obj:`Base`: iterator of bases
        """
        return self.base_seq.__iter__()

    def __reversed__(self):
        """ Get reverse iterator over base sequence 

        Returns:
            :obj:`iterator` of :obj:`Base`: iterator of bases
        """
        return self.base_seq.__reversed__()

    def __contains__(self, base):
        """ Determine if a base is in the form

        Args:
            base (:obj:`Base`): base

        Returns:
            :obj:`bool`: true if the base is in the sequence
        """
        return self.base_seq.__contains__(base)

    def __len__(self):
        """ Get the length of the sequence of the form

        Returns:
            :obj:`int`: length
        """
        return len(self.base_seq)

    def get_base_counts(self):
        """ Get the frequency of each base within the biopolymer

        Returns:
            :obj:`dict`: dictionary that maps bases to their counts
        """
        return self.base_seq.get_base_counts()

    def protonate(self, ph):
        """ Update to the major protonation state of each modification at the pH 

        Args:
            ph (:obj:`float`): pH
        """
        for base in set(self.base_seq):
            base.protonate(ph)

    def get_formula(self):
        """ Get the chemical formula

        Returns:
            :obj:`EmpiricalFormula`: chemical formula
        """
        formula = EmpiricalFormula()
        for base, count in self.get_base_counts().items():
            formula += base.get_formula() * count
        return formula + self.bond_formula * (len(self) - 1)

    def get_mol_wt(self):
        """ Get the molecular weight

        Returns:
            :obj:`float`: molecular weight
        """
        mol_wt = 0.
        for base, count in self.get_base_counts().items():
            mol_wt += base.get_mol_wt() * count
        return mol_wt + self._bond_mol_wt * (len(self) - 1)

    def get_charge(self):
        """ Get the charge

        Returns:
            :obj:`int`: charge
        """
        charge = 0
        for base, count in self.get_base_counts().items():
            charge += base.get_charge() * count
        return charge + self.bond_charge * (len(self) - 1)

    def __str__(self):
        """ Get a string representation of the biopolymer form

        Returns:
            :obj:`str`: string representation of the biopolymer form
        """
        alphabet_bases = {base: chars for chars, base in self.alphabet.items()}
        val = ''
        for base in self.base_seq:
            chars = alphabet_bases.get(base, None)
            if chars:
                val += chars
            else:
                val += str(base)
        return val

    _parser = lark.Lark(
        ''' ?start: seq

            seq: base+
            ?base: alphabet_base | inline_base
            alphabet_base: CHARS
            inline_base: "[" WS* inline_base_attr (ATTR_SEP inline_base_attr)* WS* "]"
            ?inline_base_attr: id | name | synonym | identifier | structure | delta_mass | delta_charge | position | comments
            ?id: "id" FIELD_SEP WS* ESCAPED_STRING
            ?name: "name" FIELD_SEP WS* ESCAPED_STRING
            ?synonym: "synonym" FIELD_SEP WS* ESCAPED_STRING
            ?identifier: "identifier" FIELD_SEP WS* identifier_ns "/" identifier_id
            ?identifier_ns: /[A-Za-z0-9_\.\-]+/
            ?identifier_id: /[A-Za-z0-9_\.\-:]+/
            ?structure: "structure" FIELD_SEP WS* INCHI            
            ?delta_mass: "delta-mass" FIELD_SEP WS* DALTON
            ?delta_charge: "delta-charge" FIELD_SEP WS* CHARGE
            ?position: "position" FIELD_SEP WS* START_POSITION? WS* "-" WS* END_POSITION?
            ?comments: "comments" FIELD_SEP WS* ESCAPED_STRING
            ATTR_SEP: WS* "|" WS*
            FIELD_SEP: ":"
            CHARS: /[A-Z][a-z0-9_]*/
            INCHI: /InChI=1S\/[A-Za-z0-9\(\)\-\+,\/]+/
            DALTON: /[\-\+]?[0-9]+(\.[0-9]*)?/
            CHARGE: /[\-\+]?[0-9]+/
            START_POSITION: INT
            END_POSITION: INT
            %import common.WS
            %import common.ESCAPED_STRING
            %import common.INT
            ''')

    @classmethod
    def from_str(cls, str):
        """ Create biopolymer form its string representation

        Args:
            str (:obj:`str`): string representation of the biopolymer

        Returns:
            :obj:`BpForm`: biopolymer form
        """
        class ParseTreeTransformer(lark.Transformer):
            def __init__(self, bp_form_cls):
                super(ParseTreeTransformer, self).__init__()
                self.bp_form_cls = bp_form_cls

            @lark.v_args(inline=True)
            def seq(self, *base_seq):
                return self.bp_form_cls(base_seq=base_seq)

            @lark.v_args(inline=True)
            def alphabet_base(self, chars):
                base = self.bp_form_cls.DEFAULT_ALPHABET.get(chars, None)
                if base is None:
                    raise ValueError('"{}" not in alphabet'.format(chars))
                return base

            @lark.v_args(inline=True)
            def inline_base(self, *args):
                kwargs = {
                    'synonyms': SynonymSet(),
                    'identifiers': IdentifierSet(),
                }
                for arg in args:
                    if isinstance(arg, tuple):
                        arg_name, arg_val = arg
                        if arg_name in ['id', 'name', 'structure', 'delta_mass', 'delta_charge', 'position', 'comments']:
                            if arg_name in kwargs:
                                raise ValueError('{} attribute cannot be repeated'.format(arg_name))
                            if arg_name == 'position':
                                kwargs['start_position'], kwargs['end_position'] = arg_val
                            else:
                                kwargs[arg_name] = arg_val
                        elif arg_name in ['synonyms', 'identifiers']:
                            kwargs[arg_name].add(arg_val)
                return Base(**kwargs)

            @lark.v_args(inline=True)
            def id(self, *args):
                return ('id', args[-1].value[1:-1])

            @lark.v_args(inline=True)
            def name(self, *args):
                return ('name', args[-1].value[1:-1])

            @lark.v_args(inline=True)
            def synonym(self, *args):
                return ('synonyms', args[-1].value[1:-1])

            @lark.v_args(inline=True)
            def identifier(self, *args):
                return ('identifiers', Identifier(args[-2].value, args[-1].value))

            @lark.v_args(inline=True)
            def structure(self, *args):
                return ('structure', args[-1].value)

            @lark.v_args(inline=True)
            def delta_mass(self, *args):
                return ('delta_mass', float(args[-1].value))

            @lark.v_args(inline=True)
            def delta_charge(self, *args):
                return ('delta_charge', int(float(args[-1].value)))

            @lark.v_args(inline=True)
            def position(self, *args):
                start_position = None
                end_position = None
                for arg in args:
                    if arg.type == 'START_POSITION':
                        start_position = int(float(arg.value))
                    elif arg.type == 'END_POSITION':
                        end_position = int(float(arg.value))

                return ('position', (start_position, end_position))

            @lark.v_args(inline=True)
            def comments(self, *args):
                return ('comments', args[-1].value[1:-1])

        tree = cls._parser.parse(str)
        parse_tree_transformer = ParseTreeTransformer(cls)
        return parse_tree_transformer.transform(tree)
